from typing import Optional

from data.owners import Owner
import services.data_service as svc

active_account: Optional[Owner] = None

# Is to make sure that when we reload the account we are working with the updated version
def reload_account():
    global active_account
    if not active_account:
        return

    active_account = svc.find_account_by_email(active_account.email)
