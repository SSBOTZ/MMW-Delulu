import logging
from pyrogram import Client, filters, enums
from info import (
    ADMINS,
    DATABASE_URI, DATABASE_NAME,
    SECONDDB_URI, THIRDDB_URI, FOURTHDB_URI, FIFTHDB_URI,
    COLLECTION_NAME
)
import motor.motor_asyncio
import pymongo
from pymongo.errors import BulkWriteError
from database.ia_filterdb import (
    db as clientDB,
    db2 as clientDB2,
    db3 as clientDB3,
    db4 as clientDB4,
    db5 as clientDB5,
    Media, Media2, Media3, Media4, Media5,
    choose_mediaDB,
    save_file
)

logger = logging.getLogger(__name__)

DB_REGISTRY = {
    "DATABASE_URI":  (DATABASE_URI,   DATABASE_NAME),
    "DATABASE_URI2": (SECONDDB_URI,   DATABASE_NAME),
    "DATABASE_URI3": (THIRDDB_URI,    DATABASE_NAME),
    "DATABASE_URI4": (FOURTHDB_URI,   DATABASE_NAME),
    "DATABASE_URI5": (FIFTHDB_URI,    DATABASE_NAME),
    # Short aliases
    "DB1": (DATABASE_URI,  DATABASE_NAME),
    "DB2": (SECONDDB_URI,  DATABASE_NAME),
    "DB3": (THIRDDB_URI,   DATABASE_NAME),
    "DB4": (FOURTHDB_URI,  DATABASE_NAME),
    "DB5": (FIFTHDB_URI,   DATABASE_NAME),
    # Media collection aliases (point to their host DB URI)
    "Media":  (DATABASE_URI,  DATABASE_NAME),
    "Media2": (SECONDDB_URI,  DATABASE_NAME),
    "Media3": (THIRDDB_URI,   DATABASE_NAME),
    "Media4": (FOURTHDB_URI,  DATABASE_NAME),
    "Media5": (FIFTHDB_URI,   DATABASE_NAME),
}

ALL_DB_KEYS = ["DATABASE_URI", "DATABASE_URI2", "DATABASE_URI3", "DATABASE_URI4", "DATABASE_URI5"]

STANDARD_COLLECTIONS = [COLLECTION_NAME, "users", "filters", "channels"]

def _resolve_db(label: str):
    """
    Resolve a label to (uri, db_name).
    Accepts registry keys OR raw MongoDB URIs.
    """
    label = label.strip()
    upper = label.upper()
    # Registry lookup (case-insensitive key match)
    for key, val in DB_REGISTRY.items():
        if key.upper() == upper:
            uri, db_name = val
            if not uri:
                return None, db_name, f"⚠️ URI for `{label}` is not configured."
            return uri, db_name, None
    # Raw URI fallback
    if label.startswith("mongodb"):
        return label, DATABASE_NAME, None
    return None, None, f"❓ Unknown DB label `{label}`. Use a registry key or a full MongoDB URI."


def _get_motor_db(uri: str, db_name: str):
    client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    return client, client[db_name]


async def _copy_collections_async(src_db, dst_db, collections: list, status_cb):
    """
    Copy a list of collections from src_db → dst_db.
    Calls status_cb(text) for live updates.
    Returns (total_copied, results_lines[])
    """
    results = []
    total_copied = 0

    for coll_name in collections:
        src_coll = src_db[coll_name]
        dst_coll = dst_db[coll_name]
        line = f"\n  📂 <code>{coll_name}</code> → "

        try:
            count = await src_coll.count_documents({})
            if count == 0:
                line += "⚠️ Empty, skipped."
                results.append(line)
                await status_cb(line)
                continue

            batch_size = 5000
            inserted_total = 0
            batch = []

            async for doc in src_coll.find({}):
                batch.append(doc)
                if len(batch) >= batch_size:
                    try:
                        await dst_coll.insert_many(batch, ordered=False)
                        inserted_total += len(batch)
                    except BulkWriteError as bwe:
                        inserted_total += bwe.details.get('nInserted', 0)
                        logger.warning(f"⚡ BulkWriteError (duplicates skipped) in {coll_name}")
                    batch = []

            if batch:
                try:
                    await dst_coll.insert_many(batch, ordered=False)
                    inserted_total += len(batch)
                except BulkWriteError as bwe:
                    inserted_total += bwe.details.get('nInserted', 0)
                    logger.warning(f"⚡ BulkWriteError (duplicates skipped) in {coll_name} (final batch)")

            total_copied += inserted_total
            line += f"✅ {inserted_total}/{count} docs inserted."
            logger.info(f"✅ Copied collection '{coll_name}': {inserted_total}/{count} docs.")

        except Exception as e:
            line += f"❌ Failed: {e}"
            logger.error(f"❌ Failed to copy collection '{coll_name}': {e}")

        results.append(line)
        await status_cb(line)

    return total_copied, results


HELP_TEXT = (
    "📖 <b>Usage:</b>\n"
    "<code>/copydb &lt;from&gt; &lt;to&gt;</code>\n\n"
    "<b>Examples:</b>\n"
    "• <code>/copydb Media Media2</code>\n"
    "• <code>/copydb DATABASE_URI DATABASE_URI2</code>\n"
    "• <code>/copydb all DATABASE_URI5</code>\n"
    "• <code>/copydb all mongodb+srv://...</code>\n\n"
    "<b>Registered labels:</b>\n"
    + "\n".join(f"  • <code>{k}</code>" for k in DB_REGISTRY)
)


@Client.on_message(filters.command('copydb') & filters.user(ADMINS))
async def copy_db_command(client, message):
    args = message.command[1:]

    # ── Show help if no args ──
    if not args:
        await message.reply(HELP_TEXT, parse_mode=enums.ParseMode.HTML)
        return

    if len(args) < 2:
        await message.reply(
            "❌ Need exactly 2 arguments: <code>/copydb &lt;from&gt; &lt;to&gt;</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    from_label = args[0]
    to_label   = args[1]

    msg = await message.reply(
        "⏳ <b>Initializing copy job…</b>",
        parse_mode=enums.ParseMode.HTML
    )

    # ── Resolve destination ──
    dst_uri, dst_db_name, dst_err = _resolve_db(to_label)
    if dst_err:
        await msg.edit(f"❌ Destination error: {dst_err}", parse_mode=enums.ParseMode.HTML)
        return

    try:
        dst_client, dst_db = _get_motor_db(dst_uri, dst_db_name)
        await dst_db.command("ping")
        logger.info(f"🔗 Connected to destination DB: {to_label}")
    except Exception as e:
        logger.error(f"❌ Cannot connect to destination '{to_label}': {e}")
        await msg.edit(
            f"❌ Cannot connect to destination <code>{to_label}</code>:\n<code>{e}</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    # ── "all" source: copy every configured DB → destination ──
    if from_label.lower() == "all":
        header = (
            f"🚀 <b>CopyDB — ALL → {to_label}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        live_text = [header]

        async def push(line):
            live_text.append(line)
            await msg.edit("".join(live_text), parse_mode=enums.ParseMode.HTML)

        grand_total = 0
        for db_key in ALL_DB_KEYS:
            src_uri, src_db_name, src_err = _resolve_db(db_key)
            if src_err or not src_uri:
                line = f"\n⏭️ <b>{db_key}</b>: not configured, skipped."
                await push(line)
                logger.info(f"⏭️ {db_key} skipped (not configured).")
                continue

            src_client, src_db = _get_motor_db(src_uri, src_db_name)
            try:
                collections = await src_db.list_collection_names()
            except Exception as e:
                line = f"\n❌ <b>{db_key}</b>: connect failed — {e}"
                await push(line)
                logger.error(f"❌ {db_key} connect failed: {e}")
                continue

            section = f"\n\n🗄️ <b>{db_key}</b> ({len(collections)} collections):"
            await push(section)
            logger.info(f"🗄️ Copying {db_key}: {collections}")

            copied, _ = await _copy_collections_async(src_db, dst_db, collections, push)
            grand_total += copied
            src_client.close()

        summary = (
            f"\n\n{'━'*22}\n"
            f"🏁 <b>All done!</b> {grand_total:,} docs copied → <code>{to_label}</code>"
        )
        await push(summary)
        logger.info(f"🏁 copydb all → {to_label}: {grand_total} total docs.")
        dst_client.close()
        return

    # ── Single source ──
    src_uri, src_db_name, src_err = _resolve_db(from_label)
    if src_err:
        await msg.edit(f"❌ Source error: {src_err}", parse_mode=enums.ParseMode.HTML)
        return

    try:
        src_client, src_db = _get_motor_db(src_uri, src_db_name)
        collections = await src_db.list_collection_names()
        logger.info(f"🔗 Connected to source DB: {from_label} — {len(collections)} collections found.")
    except Exception as e:
        logger.error(f"❌ Cannot connect to source '{from_label}': {e}")
        await msg.edit(
            f"❌ Cannot connect to source <code>{from_label}</code>:\n<code>{e}</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    header = (
        f"🔄 <b>CopyDB — {from_label} → {to_label}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 {len(collections)} collection(s) found.\n"
    )
    live_text = [header]

    async def push(line):
        live_text.append(line)
        await msg.edit("".join(live_text), parse_mode=enums.ParseMode.HTML)

    total_copied, _ = await _copy_collections_async(src_db, dst_db, collections, push)

    summary = (
        f"\n\n{'━'*22}\n"
        f"✅ <b>Done!</b> {total_copied:,} docs copied.\n"
        f"📤 <b>Source:</b> <code>{from_label}</code>\n"
        f"📥 <b>Dest:</b>   <code>{to_label}</code>"
    )
    await push(summary)
    logger.info(f"✅ copydb {from_label} → {to_label}: {total_copied} total docs.")

    src_client.close()
    dst_client.close()

