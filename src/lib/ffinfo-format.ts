const PET_NAMES: Record<number, string> = {
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
};

function unix(ts?: number | string) {
  if (!ts) return "N/A";
  return new Date(Number(ts) * 1000).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });
}

function cleanEnum(v?: string) {
  if (!v) return "N/A";
  return v
    .replace(
      /(GENDER|LANGUAGE|TIMEACTIVE|MODEPREFER|RANKSHOW|REWARDSTATE|EXTERNALICONSTATUS|EXTERNALICONSHOWTYPE)/g,
      "",
    )
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function creditStatus(score?: number) {
  if (typeof score !== "number") return "Unknown";
  if (score >= 90) return "Excellent 🟢";
  if (score >= 70) return "Good 🟡";
  if (score >= 50) return "Average 🟠";
  return "Low 🔴";
}

export function petName(id?: number) {
  return (id !== undefined && PET_NAMES[id]) || "Unknown";
}

export function buildSummary(data: Record<string, any>, serverKey: string) {
  const b = data["basicinfo"] ?? {};
  const pr = data["profileinfo"] ?? {};
  const p = data["petinfo"] ?? {};
  const s = data["socialinfo"] ?? {};
  const c = data["creditscoreinfo"] ?? {};
  const clan = data["clanbasicinfo"] ?? {};
  const sep = "━━━━━━━━━━━━━";
  const score = c.creditscore;

  return [
    `🌍 Server: ${serverKey}`,
    "",
    sep,
    "👤 ACCOUNT",
    `• Nickname: ${b.nickname}`,
    `• UID: ${b.accountid}`,
    `• Region: ${b.region}`,
    `• Account Type: ${b.accounttype}`,
    `• Level: ${b.level}`,
    `• EXP: ${b.exp}`,
    `• Likes: ❤️ ${b.liked}`,
    `• Title ID: ${b.title}`,
    `• Banner ID: ${b.bannerid}`,
    `• Avatar Frame: ${b.avatarframe}`,
    `• Created: ${unix(b.createat)}`,
    `• Last Login: ${unix(b.lastloginat)}`,
    `• Game Version: ${b.releaseversion}`,
    "",
    sep,
    "🎖 BADGES",
    `• Total Badges: ${b.badgecnt}`,
    `• Badge ID: ${b.badgeid}`,
    "",
    sep,
    "🏆 RANKS",
    `• BR Rank: ${b.rank}`,
    `• BR Points: ${b.rankingpoints}`,
    `• Max BR Rank: ${b.maxrank}`,
    `• CS Rank: ${b.csrank}`,
    `• CS Points: ${b.csrankingpoints}`,
    `• Max CS Rank: ${b.csmaxrank}`,
    `• Season ID: ${b.seasonid}`,
    "",
    sep,
    "🎯 ADVANCED RANK DATA",
    `• Hippo Rank: ${b.hipporank}`,
    `• Hippo Points: ${b.hipporankingpoints}`,
    `• CS Peak Tournament Rank: ${b.cspeaktournamentrankpos}`,
    "",
    sep,
    "🧬 PROFILE",
    `• Avatar ID: ${pr.avatarid}`,
    `• Head Pic ID: ${b.headpic}`,
    `• Equipped Skills Count: ${pr.equipedskills?.length || 0}`,
    `• Skill IDs: ${pr.equipedskills?.join(", ") || "N/A"}`,
    `• Clothes Count: ${pr.clothes?.length || 0}`,
    `• PvE Weapon: ${pr.pveprimaryweapon}`,
    "",
    sep,
    "🐾 PET",
    `• Name: ${petName(p.id)}`,
    `• Pet ID: ${p.id || "N/A"}`,
    `• Level: ${p.level || "N/A"}`,
    `• EXP: ${p.exp || "N/A"}`,
    `• Skin ID: ${p.skinid || "N/A"}`,
    `• Skill ID: ${p.selectedskillid || "N/A"}`,
    `• Selected: ${p.isselected ? "Yes" : "No"}`,
    "",
    sep,
    "🏰 CLAN",
    `• Clan Name: ${clan.clanname || "Not in clan"}`,
    `• Clan ID: ${clan.clanid || "N/A"}`,
    `• Clan Level: ${clan.clanlevel || "N/A"}`,
    "",
    sep,
    "🌐 SOCIAL",
    `• Gender: ${cleanEnum(s.gender)}`,
    `• Language: ${cleanEnum(s.language)}`,
    `• Active Time: ${cleanEnum(s.timeactive)}`,
    `• Preferred Mode: ${cleanEnum(s.modeprefer)}`,
    `• Rank Show Mode: ${cleanEnum(s.rankshow)}`,
    "",
    "📝 SIGNATURE",
    s.signature || "None",
    "",
    sep,
    "🛡 TRUST & SECURITY",
    `• Credit Score: ${score || "N/A"}`,
    `• Credit Status: ${creditStatus(score)}`,
    `• Reward State: ${cleanEnum(c.rewardstate)}`,
    `• Period Ends: ${unix(c.periodicsummaryendtime)}`,
    `• Safe Account: ${
      typeof score === "number" ? (score >= 90 ? "Yes ✅" : "No ⚠️") : "Unknown"
    }`,
    "",
    sep,
    "📦 VISIBILITY",
    `• Show BR Rank: ${b.showbrrank}`,
    `• Show CS Rank: ${b.showcsrank}`,
    `• Weapon Skins Shown: ${b.weaponskinshows?.length || 0}`,
    "",
  ].join("\n");
}
