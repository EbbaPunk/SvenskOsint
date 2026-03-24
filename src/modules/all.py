

# Medier
from .sweden.media.aftonbladet import aftonbladet
from .sweden.media.expressen import expressen
from .sweden.media.samnytt import samnytt
from .sweden.media.dn import dn
from .sweden.media.di import di
from .sweden.media.tv4 import tv4
from .sweden.media.omni import omni
from .sweden.media.svd import svd

# Marketplace
from .sweden.marketplace.blocket import blocket
from .sweden.marketplace.hemnet import hemnet
from .sweden.marketplace.bytbil import bytbil

# Online butik
from .sweden.retail.willys import willys
from .sweden.retail.systembolaget import systembolaget
from .sweden.retail.elgiganten import elgiganten
from .sweden.retail.inet import inet
from .sweden.retail.komplett import komplett
from .sweden.retail.seven_eleven import seven_eleven
from .sweden.retail.pressbyran import pressbyran
from .sweden.retail.foodora import foodora
from .sweden.retail.power import power
from .sweden.retail.nelly import nelly
from .sweden.retail.cocopanda import cocopanda
from .sweden.retail.ammocenter import ammocenter

# Community
from .sweden.community.byggahus import byggahus
from .sweden.community.loveable import loveable
from .sweden.community.jagareforbundet import jagareforbundet
from .sweden.community.utsidan import utsidan
from .sweden.community.allsvenskan import allsvenskan

#Politik
from .sweden.political.mp import mp
from .sweden.political.zetk import zetk
from .sweden.political.liberalerna import liberalerna

# Ryskt
from .russia.mailru import mail_ru
from .russia.rambler import rambler

# UK
from .uk.deliveroo import deliveroo

#USA
from .us.adobe import adobe
from .us.archive import archive
from .us.bible import bibledotcom
from .us.bodybuilding import bodybuilding
from .us.flickr import flickr
from .us.insightly import insightly
from .us.lastpass import lastpass
from .us.medal import medal
from .us.microsoft import microsoft_recovery
from .us.office365 import office365
from .us.teamtreehouse import teamtreehouse
from .us.vimeo import vimeo

# GLOBALT
from .global_.lovense import lovense
from .global_.xvideos import xvideos
from .global_.plurk import plurk
from .global_.w3schools import w3schools
from .global_.freelancer import freelancer
#############################################
#############################################

from concurrent.futures import ThreadPoolExecutor, as_completed


def _modules():
    return [
        ("aftonbladet", aftonbladet),
        ("expressen", expressen),
        ("samnytt", samnytt),
        ("dn", dn),
        ("di", di),
        ("blocket", blocket),
        ("hemnet", hemnet),
        ("systembolaget", systembolaget),
        ("elgiganten", elgiganten),
        ("inet", inet),
        ("bytbil", bytbil),
        ("byggahus", byggahus),
        ("lovable", loveable),
        ("Jägarförbundet", jagareforbundet),
        ("Jägarförbundet/SSN", jagareforbundet),
        ("utsidan", utsidan),
        ("allsvenskan", allsvenskan),
        ("tv4", tv4),
        ("Miljöpartiet", mp),
        ("zetk/Vänsterpartiet", zetk),
        ("Liberalerna", liberalerna),
        ("mail.ru", mail_ru),
        ("rambler", rambler),
        ("deliveroo", deliveroo),
        ("adobe", adobe),
        ("archive.org", archive),
        ("bible", bibledotcom),
        ("bodybuilding", bodybuilding),
        ("flickr", flickr),
        ("insightly", insightly),
        ("lastpass", lastpass),
        ("medal", medal),
        ("microsoft", microsoft_recovery),
        ("office365", office365),
        ("teamtreehouse", teamtreehouse),
        ("vimeo", vimeo),
        ("lovense", lovense),
        ("xvideos", xvideos),
        ("plurk", plurk),
        ("w3schools", w3schools),
        ("freelancer", freelancer),
        ("omni", omni),
        ("svd", svd),
        ("komplett", komplett),
        ("7-Eleven", seven_eleven),
        ("Pressbyrån", pressbyran),
        ("foodora", foodora),
        ("power", power),
        ("nelly", nelly),
        ("cocopanda", cocopanda),
        ("ammocenter", ammocenter),
    ]


def check_all(email: str, personnummer: str = "") -> dict:
    modules = _modules()
    results = {}

    def run(name, fn, arg):
        try:
            result = fn(arg)
            if isinstance(result, dict) and "accountExists" not in result and "exists" in result:
                result["accountExists"] = result.pop("exists")
            return name, result
        except Exception as e:
            return name, {"accountExists": False, "error": str(e)}

    SSN_MODULES = {"willys", "Jägarförbundet/SSN"}

    with ThreadPoolExecutor(max_workers=len(modules)) as pool:
        futures = {
            pool.submit(
                run, name, fn, personnummer if name in SSN_MODULES else email
            ): name
            for name, fn in modules
        }
        for future in as_completed(futures):
            try:
                name, data = future.result(timeout=30)
            except TimeoutError:
                name = futures[future]
                data = {"accountExists": False, "error": "timeout"}
            results[name] = data

    return results
