from app.db.models.processing_job import ProcessingJob
from app.db.models.report import Report
from app.db.models.upload import Upload
from app.db.models.user import User
from app.services.activity_service import log_activity


async def list_upload_history(user: User) -> list[Upload]:
    return await Upload.find(Upload.user_id == user.id).sort(-Upload.created_at).to_list()


async def list_job_history(user: User) -> list[ProcessingJob]:
    return await ProcessingJob.find(ProcessingJob.user_id == user.id).sort(-ProcessingJob.created_at).to_list()


async def list_report_history(user: User) -> list[Report]:
    return await Report.find(Report.user_id == user.id).sort(-Report.created_at).to_list()


async def list_user_activity(user: User, limit: int = 50):
    from app.db.models.activity import UserActivity

    activities = (
        await UserActivity.find(UserActivity.user_id == user.id)
        .sort(-UserActivity.created_at)
        .limit(limit)
        .to_list()
    )
    await log_activity(user.id, "history_viewed")
    return activities
