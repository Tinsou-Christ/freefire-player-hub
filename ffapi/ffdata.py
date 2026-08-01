"""Données de référence et helpers de formatage pour l'API Free Fire Info."""

from datetime import datetime, timedelta, timezone

UPSTREAM_INFO_URL = "https://ffapii.vercel.app/get_player_personal_show"
UPSTREAM_IMAGE_URL = "https://profile.thug4ff.com/api/profile"

SERVERS = {
    "SG": "sg",
    "BD": "bd",
    "RU": "ru",
    "ID": "id",
    "TW": "tw",
    "US": "us",
    "VN": "vn",
    "TH": "th",
    "ME": "me",
    "PK": "pk",
    "CIS": "cis",
    "BR": "br",
    "IND": "ind",
}

PET_NAMES = {
    1300000041: "Falco",
    1300000042: "Ottero",
    1300000043: "Mr. Waggor",
    1300000044: "Poring",
    1300000045: "Detective Panda",
    1300000046: "Night Panther",
    1300000047: "Beaston",
    1300000048: "Rockie",
    1300000049: "Moony",
    1300000050: "Dreki",
    1300000051: "Arvon",
}

IST = timezone(timedelta(hours=5, minutes=30))

_ENUM_PREFIXES = (
    "GENDER",
    "LANGUAGE",
    "TIMEACTIVE",
    "MODEPREFER",
    "RANKSHOW",
    "REWARDSTATE",
    "EXTERNALICONSTATUS",
    "EXTERNALICONSHOWTYPE",
)


def unix(ts):
    if not ts:
        return "N/A"
    try:
        return datetime.fromtimestamp(int(ts), IST).strftime("%d/%m/%Y, %H:%M:%S")
    except (ValueError, TypeError, OSError):
        return "N/A"


def clean_enum(value):
    if not value:
        return "N/A"
    out = str(value)
    for prefix in _ENUM_PREFIXES:
        out = out.replace(prefix, "")
    return out.replace("_", " ").strip().lower().title()


def credit_status(score):
    if not isinstance(score, int):
        return "Unknown"
    if score >= 90:
        return "Excellent 🟢"
    if score >= 70:
        return "Good 🟡"
    if score >= 50:
        return "Average 🟠"
    return "Low 🔴"


def build_summary(data, server_key):
    """Reproduit exactement le rendu texte de la commande `ffinfo`."""
    b = data.get("basicinfo") or {}
    pr = data.get("profileinfo") or {}
    p = data.get("petinfo") or {}
    s = data.get("socialinfo") or {}
    c = data.get("creditscoreinfo") or {}
    clan = data.get("clanbasicinfo") or {}

    pet_name = PET_NAMES.get(p.get("id"), "Unknown")
    skills = pr.get("equipedskills") or []
    score = c.get("creditscore")
    safe = "Unknown"
    if isinstance(score, int):
        safe = "Yes ✅" if score >= 90 else "No ⚠️"

    sep = "━━━━━━━━━━━━━"
    return "\n".join(
        [
            f"🌍 Server: {server_key}",
            "",
            sep,
            "👤 ACCOUNT",
            f"• Nickname: {b.get('nickname')}",
            f"• UID: {b.get('accountid')}",
            f"• Region: {b.get('region')}",
            f"• Account Type: {b.get('accounttype')}",
            f"• Level: {b.get('level')}",
            f"• EXP: {b.get('exp')}",
            f"• Likes: ❤️ {b.get('liked')}",
            f"• Title ID: {b.get('title')}",
            f"• Banner ID: {b.get('bannerid')}",
            f"• Avatar Frame: {b.get('avatarframe')}",
            f"• Created: {unix(b.get('createat'))}",
            f"• Last Login: {unix(b.get('lastloginat'))}",
            f"• Game Version: {b.get('releaseversion')}",
            "",
            sep,
            "🎖 BADGES",
            f"• Total Badges: {b.get('badgecnt')}",
            f"• Badge ID: {b.get('badgeid')}",
            "",
            sep,
            "🏆 RANKS",
            f"• BR Rank: {b.get('rank')}",
            f"• BR Points: {b.get('rankingpoints')}",
            f"• Max BR Rank: {b.get('maxrank')}",
            f"• CS Rank: {b.get('csrank')}",
            f"• CS Points: {b.get('csrankingpoints')}",
            f"• Max CS Rank: {b.get('csmaxrank')}",
            f"• Season ID: {b.get('seasonid')}",
            "",
            sep,
            "🎯 ADVANCED RANK DATA",
            f"• Hippo Rank: {b.get('hipporank')}",
            f"• Hippo Points: {b.get('hipporankingpoints')}",
            f"• CS Peak Tournament Rank: {b.get('cspeaktournamentrankpos')}",
            "",
            sep,
            "🧬 PROFILE",
            f"• Avatar ID: {pr.get('avatarid')}",
            f"• Head Pic ID: {b.get('headpic')}",
            f"• Equipped Skills Count: {len(skills)}",
            f"• Skill IDs: {', '.join(str(x) for x in skills) if skills else 'N/A'}",
            f"• Clothes Count: {len(pr.get('clothes') or [])}",
            f"• PvE Weapon: {pr.get('pveprimaryweapon')}",
            "",
            sep,
            "🐾 PET",
            f"• Name: {pet_name}",
            f"• Pet ID: {p.get('id') or 'N/A'}",
            f"• Level: {p.get('level') or 'N/A'}",
            f"• EXP: {p.get('exp') or 'N/A'}",
            f"• Skin ID: {p.get('skinid') or 'N/A'}",
            f"• Skill ID: {p.get('selectedskillid') or 'N/A'}",
            f"• Selected: {'Yes' if p.get('isselected') else 'No'}",
            "",
            sep,
            "🏰 CLAN",
            f"• Clan Name: {clan.get('clanname') or 'Not in clan'}",
            f"• Clan ID: {clan.get('clanid') or 'N/A'}",
            f"• Clan Level: {clan.get('clanlevel') or 'N/A'}",
            "",
            sep,
            "🌐 SOCIAL",
            f"• Gender: {clean_enum(s.get('gender'))}",
            f"• Language: {clean_enum(s.get('language'))}",
            f"• Active Time: {clean_enum(s.get('timeactive'))}",
            f"• Preferred Mode: {clean_enum(s.get('modeprefer'))}",
            f"• Rank Show Mode: {clean_enum(s.get('rankshow'))}",
            "",
            "📝 SIGNATURE",
            s.get("signature") or "None",
            "",
            sep,
            "🛡 TRUST & SECURITY",
            f"• Credit Score: {score or 'N/A'}",
            f"• Credit Status: {credit_status(score)}",
            f"• Reward State: {clean_enum(c.get('rewardstate'))}",
            f"• Period Ends: {unix(c.get('periodicsummaryendtime'))}",
            f"• Safe Account: {safe}",
            "",
            sep,
            "📦 VISIBILITY",
            f"• Show BR Rank: {b.get('showbrrank')}",
            f"• Show CS Rank: {b.get('showcsrank')}",
            f"• Weapon Skins Shown: {len(b.get('weaponskinshows') or [])}",
            "",
        ]
    )
