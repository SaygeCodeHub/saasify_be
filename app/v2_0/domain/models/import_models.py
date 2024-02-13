"""Table creation"""
from app.v2_0.domain.models import user_auth, user_details, user_documents, user_finance, user_company_branch, \
    companies, branches, branch_settings, leaves, module_subscriptions, user_official_details, user_bank_details, tasks, \
    announcements, shifts
from app.v2_0.infrastructure.database import engine
from app.v2_0.domain.models.user_auth import Base

user_auth.Base.metadata.create_all(bind=engine)
user_details.Base.metadata.create_all(bind=engine)
user_documents.Base.metadata.create_all(bind=engine)
user_finance.Base.metadata.create_all(bind=engine)
user_company_branch.Base.metadata.create_all(bind=engine)
companies.Base.metadata.create_all(bind=engine)
branches.Base.metadata.create_all(bind=engine)
branch_settings.Base.metadata.create_all(bind=engine)
leaves.Base.metadata.create_all(bind=engine)
module_subscriptions.Base.metadata.create_all(bind=engine)
user_official_details.Base.metadata.create_all(bind=engine)
user_bank_details.Base.metadata.create_all(bind=engine)
tasks.Base.metadata.create_all(bind=engine)
announcements.Base.metadata.create_all(bind=engine)
shifts.Base.metadata.create_all(bind=engine)
