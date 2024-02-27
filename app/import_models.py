"""Table creation"""
from app.v2_0.HRMS.domain.models import user_auth, user_documents, user_finance, companies, branches, branch_settings, \
    leaves, \
    user_official_details, user_bank_details, announcements
from app.v2_0.HRMS.domain.models import module_subscriptions, user_details, shifts, user_company_branch, tasks
from app.v2_0.POS.domain.models import categories, product_variants, products, orders
from app.infrastructure.database import engine

"""=========================================================HRMS============================================================="""
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

"""=========================================================POS============================================================="""
categories.Base.metadata.create_all(bind=engine)
product_variants.Base.metadata.create_all(bind=engine)
products.Base.metadata.create_all(bind=engine)
orders.Base.metadata.create_all(bind=engine)
