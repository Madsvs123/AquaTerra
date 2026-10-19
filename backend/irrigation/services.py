from datetime import timedelta
from decimal import Decimal

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from common.choices import RunSource, RunStatus
from irrigation.models import IrrigationRun, WaterUsageRecord


def start_run(*, organization, zone, user=None, source=RunSource.MANUAL, minutes=15, program=None, slot=None, recommendation=None, notes=""):
    active = IrrigationRun.objects.filter(
        organization=organization, zone=zone, status__in=[RunStatus.RUNNING, RunStatus.PAUSED, RunStatus.QUEUED]
    ).first()
    if active:
        return active
    now = timezone.now()
    run = IrrigationRun.objects.create(
        organization=organization,
        zone=zone,
        farm=zone.farm,
        program=program,
        slot=slot,
        recommendation=recommendation,
        source=source,
        status=RunStatus.RUNNING,
        requested_by=user,
        scheduled_for=now,
        started_at=now,
        planned_minutes=minutes,
        notes=notes,
    )
    publish_irrigation(organization.id, run, "started")
    return run


def pause_run(run):
    if run.status != RunStatus.RUNNING:
        return run
    now = timezone.now()
    if run.started_at:
        run.elapsed_seconds += int((now - (run.paused_at or run.started_at)).total_seconds()) if run.paused_at else int(
            (now - run.started_at).total_seconds()
        )
    run.status = RunStatus.PAUSED
    run.paused_at = now
    run.save(update_fields=["status", "paused_at", "elapsed_seconds", "updated_at"])
    publish_irrigation(run.organization_id, run, "paused")
    return run


def resume_run(run):
    if run.status != RunStatus.PAUSED:
        return run
    run.status = RunStatus.RUNNING
    run.paused_at = None
    run.started_at = timezone.now()
    run.save(update_fields=["status", "paused_at", "started_at", "updated_at"])
    publish_irrigation(run.organization_id, run, "resumed")
    return run


def stop_run(run, status=RunStatus.COMPLETED):
    if run.status in {RunStatus.COMPLETED, RunStatus.CANCELLED, RunStatus.FAILED}:
        return run
    now = timezone.now()
    if run.status == RunStatus.RUNNING and run.started_at:
        run.elapsed_seconds += int((now - run.started_at).total_seconds())
    run.status = status
    run.ended_at = now
    minutes = max(run.elapsed_seconds / 60, 1)
    flow = Decimal(str(run.zone.flow_limit_lpm or 30))
    run.volume_m3 = (flow * Decimal(str(minutes)) / Decimal("1000")).quantize(Decimal("0.001"))
    run.peak_flow_lpm = flow
    run.save()
    cost_rate = Decimal(str(run.organization.water_cost_per_unit or 0))
    WaterUsageRecord.objects.create(
        organization=run.organization,
        farm=run.farm,
        field=run.zone.field,
        zone=run.zone,
        crop_type=run.zone.field.crop_type,
        run=run,
        period_start=run.started_at or run.created_at,
        period_end=now,
        volume_m3=run.volume_m3,
        cost=(run.volume_m3 * cost_rate).quantize(Decimal("0.01")),
        efficiency_percent=Decimal("92.0"),
    )
    publish_irrigation(run.organization_id, run, "stopped")
    return run


def publish_irrigation(organization_id, run, event):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    payload = {
        "type": "irrigation_event",
        "payload": {
            "event": event,
            "id": str(run.id),
            "zone": str(run.zone_id),
            "zone_name": run.zone.name,
            "status": run.status,
            "source": run.source,
            "volume_m3": float(run.volume_m3 or 0),
            "planned_minutes": run.planned_minutes,
        },
    }
    try:
        async_to_sync(channel_layer.group_send)(f"org_{organization_id}_irrigation", payload)
    except Exception:
        pass


def complete_elapsed_runs():
    now = timezone.now()
    running = IrrigationRun.objects.filter(status=RunStatus.RUNNING, started_at__isnull=False)
    for run in running:
        elapsed = run.elapsed_seconds + int((now - run.started_at).total_seconds())
        if elapsed >= run.planned_minutes * 60:
            stop_run(run)
