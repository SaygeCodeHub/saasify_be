"""Table creation"""
from app.v2_0.domain.models import user_auth, user_details, user_documents, user_finance, user_company_branch, \
    companies, branches, branch_settings, leaves
from app.v2_0.infrastructure.database import engine
from app.v2_0.infrastructure.database import Base

user_auth.Base.metadata.create_all(bind=engine)
user_details.Base.metadata.create_all(bind=engine)
user_documents.Base.metadata.create_all(bind=engine)
user_finance.Base.metadata.create_all(bind=engine)
user_company_branch.Base.metadata.create_all(bind=engine)
companies.Base.metadata.create_all(bind=engine)
branches.Base.metadata.create_all(bind=engine)
branch_settings.Base.metadata.create_all(bind=engine)
leaves.Base.metadata.create_all(bind=engine)