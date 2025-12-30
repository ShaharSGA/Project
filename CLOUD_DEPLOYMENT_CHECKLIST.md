# Streamlit Cloud Deployment Checklist

**Last Updated:** 2025-12-30
**Status:** ✅ Ready for deployment

---

## Pre-Deployment Checklist

### ✅ 1. Code Optimizations
- [x] **Token optimization** - Moved instructions to Agent backstory
- [x] **ChromaDB pre-built** - 31MB committed to git (.chromadb/)
- [x] **Embedding cache** - Prevents redundant OpenAI API calls
- [x] **Verbose=False** - Saves 60K+ tokens per run
- [x] **Campaign Bible summarization** - Function ready (optional)

### ✅ 2. Secrets Management
- [x] **config.py updated** - Uses `st.secrets` for Cloud, `.env` for local
- [x] **get_secret() function** - Handles both environments
- [x] **.gitignore** - Excludes `.env` and `.streamlit/secrets.toml`
- [x] **secrets.toml.example** - Template provided

### ✅ 3. Dependencies
- [x] **requirements.txt** - All packages listed with versions
- [x] **packages.txt** - System package (sqlite3) included
- [x] **ChromaDB 0.5.23** - Pinned version for stability

### ✅ 4. Database
- [x] **Supabase integration** - Configured in config.py
- [x] **Auto-detection** - Uses Supabase on Cloud, SQLite locally
- [x] **Schema ready** - supabase_schema_correct.sql provided

### ✅ 5. UI/UX
- [x] **RTL support** - All Hebrew content displays right-to-left
- [x] **Dark mode fixes** - Light text on dark backgrounds
- [x] **Button spacing** - Improved layout
- [x] **CSS caching** - Styles cached for performance

### ✅ 6. File Structure
- [x] **app.py** - Main entry point
- [x] **pages/** - Multi-page structure
- [x] **Data/** - Knowledge base committed to git
- [x] **.chromadb/** - Pre-built collections committed
- [x] **.streamlit/config.toml** - Streamlit configuration

---

## Deployment Steps

### Step 1: Streamlit Cloud Setup
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Select branch: `main`
4. Main file path: `app.py`

### Step 2: Configure Secrets
In Streamlit Cloud dashboard → Secrets, paste:

```toml
# OpenAI API Configuration
OPENAI_API_KEY = "sk-proj-..."
OPENAI_MODEL_NAME = "gpt-4o-mini"

# Supabase Configuration
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
```

**Required secrets:**
- ✅ `OPENAI_API_KEY` - Get from OpenAI dashboard
- ✅ `SUPABASE_URL` - Get from Supabase project settings
- ✅ `SUPABASE_KEY` - Use anon/public key (NOT service_role)

### Step 3: Supabase Database Setup
1. Create Supabase project at [supabase.com](https://supabase.com)
2. Run SQL schema from `supabase_schema_correct.sql`
3. Copy URL and anon key to Streamlit secrets
4. Verify tables created: `feedback`, `users`

### Step 4: Deploy
1. Click "Deploy!" in Streamlit Cloud
2. Wait for build (~3-5 minutes)
3. Check logs for errors

---

## Expected Performance

### ⚡ Startup Time
- **ChromaDB loading:** < 10 seconds (pre-built)
- **Total startup:** ~15-20 seconds
- **vs. Original:** 15+ minutes (building embeddings)

### 💰 Token Usage
- **Before optimization:** ~95,000 prompt tokens
- **After optimization:** ~25,000-30,000 tokens (70% reduction)
- **Cost per run:** ~$0.015 (vs $0.06 before)

### 🎯 RAG Performance
- **Embedding cache:** Prevents duplicate queries
- **ChromaDB collections:** 5 pre-built
- **Query logging:** Visible in Factory Floor

---

## Troubleshooting

### Issue: "No module named 'chromadb'"
**Solution:** Verify `requirements.txt` includes `chromadb==0.5.23`

### Issue: "OPENAI_API_KEY not found"
**Solution:** Add to Streamlit Cloud secrets (not .env)

### Issue: "No such table: feedback"
**Solution:**
1. Check SUPABASE_URL and SUPABASE_KEY in secrets
2. Run `supabase_schema_correct.sql` in Supabase SQL editor
3. Verify `USE_SUPABASE = True` in logs

### Issue: "ChromaDB PersistentClient error"
**Solution:**
1. Verify `.chromadb/` directory is committed to git
2. Check `packages.txt` includes `sqlite3`
3. Verify ChromaDB version is 0.5.23

### Issue: Dark text on dark background
**Solution:** CSS should auto-fix. If not, check `ui/styles.py` is loaded

### Issue: Text not RTL
**Solution:** CSS should auto-fix. If not, check `load_custom_css()` is called

---

## Post-Deployment Verification

### ✅ Checklist
1. [ ] App loads without errors
2. [ ] ChromaDB loads in < 10 seconds
3. [ ] All 4 pages accessible
4. [ ] Can generate content (Architect's Table → Factory Floor)
5. [ ] RAG queries show in Factory Floor
6. [ ] Token usage ~25-30K
7. [ ] Cost displayed correctly
8. [ ] Posts display in Editor's Desk
9. [ ] Feedback system works (saves to Supabase)
10. [ ] RTL text displays correctly
11. [ ] Dark mode text is readable
12. [ ] No "missing secrets" errors

---

## Critical Files for Cloud

### Must be in git:
```
app.py                          # Entry point
requirements.txt                # Python deps
packages.txt                    # System deps
.streamlit/config.toml          # Streamlit config
.streamlit/secrets.toml.example # Secrets template (NOT actual secrets!)
.chromadb/                      # Pre-built vector DB (31MB)
Data/                           # Knowledge base
pages/                          # All UI pages
agents/                         # Agent definitions
tasks/                          # Task definitions
tools/                          # RAG tools
core/                           # Core logic
ui/styles.py                    # CSS styles
config.py                       # Configuration
```

### Must NOT be in git:
```
.env                            # Local secrets
.streamlit/secrets.toml         # Actual secrets
*.db                            # SQLite databases (except .chromadb/)
__pycache__/                    # Python cache
.venv/                          # Virtual environment
```

---

## Maintenance

### Weekly:
- Monitor token usage (should stay ~25-30K)
- Check error logs in Streamlit Cloud
- Verify Supabase storage (feedback table growth)

### Monthly:
- Review ChromaDB performance
- Update dependencies if needed
- Check OpenAI API costs

### As Needed:
- Update Data/ files → Rebuild ChromaDB locally → Commit
- Add new personas → Update PersonaConfig in config.py
- Modify agent instructions → Update agents/*.py backstories

---

## Support Resources

- **Streamlit Docs:** https://docs.streamlit.io/deploy/streamlit-community-cloud
- **Supabase Docs:** https://supabase.com/docs
- **OpenAI API:** https://platform.openai.com/docs
- **ChromaDB Docs:** https://docs.trychroma.com/

---

**END OF CHECKLIST**
