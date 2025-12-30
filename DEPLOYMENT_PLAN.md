# Dana's Brain - Streamlit Cloud Deployment Plan

**Status**: 🟡 In Progress
**Last Updated**: 2025-12-29
**Repository**: ShaharSGA/Project

---

## 📋 Deployment Checklist

### Phase 1: Pre-Deployment Preparation ✅ COMPLETED

- [x] **Restore Missing Files** (from git commit 6bbb02b)
  - [x] core/auth.py
  - [x] core/content_parser.py
  - [x] core/feedback_manager.py
  - [x] core/feedback_triage.py
  - [x] ui/styles.py
  - [x] pages/1_📐_Architects_Table.py
  - [x] pages/2_🏭_Factory_Floor.py
  - [x] pages/5_📚_Feedback_Guide.py

- [x] **Update Dependencies**
  - [x] Create requirements.txt with flexible versions
  - [x] Include Supabase for persistent feedback storage
  - [x] Pin compatible versions for Streamlit Cloud

- [x] **Cloud Configuration Files**
  - [x] .python-version (Python 3.11)
  - [x] .streamlit/config.toml (server settings, theme)
  - [x] .streamlit/secrets.toml.example (secrets template)

### Phase 2: Supabase Integration ✅ COMPLETED (Code)

- [x] **Modify config.py**
  - [x] Add `is_streamlit_cloud()` detection function
  - [x] Set cloud-aware paths (/tmp for ephemeral filesystem)
  - [x] Add Supabase configuration variables
  - [x] Enable Supabase when running on cloud

- [x] **Modify feedback_manager.py**
  - [x] Import Supabase client
  - [x] Add `_get_supabase_client()` helper function
  - [x] Initialize Supabase client on cloud deployment

- [x] **Export Existing Feedback**
  - [x] Create export_feedback_to_csv.py script
  - [x] Export 43 feedback entries to feedback_export.csv

### Phase 3: Git Operations ✅ COMPLETED

- [x] **Commit All Changes**
  - [x] Commit 1: Prepare app for Streamlit Cloud deployment (ee6df1b)
  - [x] Commit 2: Fix requirements.txt for compatibility (2fef7e3)
  - [x] Commit 3: Fix sidebar menu text visibility (ccf2123)
  - [x] Commit 4: Added Dev Container Folder (44e23d8)
  - [x] Commit 5: Change layout from centered to wide (deac866)

- [x] **Push to GitHub**
  - [x] Push all commits to main branch
  - [x] Repository: https://github.com/ShaharSGA/Project

### Phase 4: Supabase Database Setup ⏳ IN PROGRESS

- [x] **Create Supabase Project**
  - [x] Project created: jszdmgcdofxz1iddvgpb.supabase.co
  - [x] Get API credentials (URL + anon key)

- [ ] **Database Schema Migration** 🔴 CURRENT STEP
  - [x] Create correct schema SQL (supabase_schema_correct.sql)
  - [ ] **ACTION REQUIRED**: Run SQL in Supabase SQL Editor
    1. Go to Supabase Dashboard → SQL Editor
    2. Paste contents of supabase_schema_correct.sql
    3. Confirm "Run this query" on destructive operation warning
    4. Verify table created successfully

- [ ] **Import Existing Feedback**
  - [ ] **ACTION REQUIRED**: Import CSV to Supabase
    1. Go to Table Editor → feedback table
    2. Click "Insert" dropdown → "Import data from CSV"
    3. Upload feedback_export.csv (43 entries)
    4. Verify import successful

### Phase 5: Streamlit Cloud Deployment ✅ COMPLETED (Partial)

- [x] **Create Deployment**
  - [x] Repository: ShaharSGA/Project
  - [x] Branch: main
  - [x] Main file: app.py
  - [x] Python version: 3.11

- [x] **Configure Secrets**
  - [x] Add OPENAI_API_KEY
  - [x] Add OPENAI_MODEL_NAME
  - [x] Add SUPABASE_URL
  - [x] Add SUPABASE_KEY

- [x] **Fix Initial Errors**
  - [x] Fix requirements.txt version conflicts
  - [x] Fix sidebar text visibility (CSS)
  - [x] Fix layout width (centered → wide)

- [ ] **Final Reboot** 🔴 PENDING
  - [ ] **ACTION REQUIRED**: After Supabase schema + CSV import
    1. Reboot Streamlit Cloud app
    2. Test feedback system writes to Supabase
    3. Verify all pages load correctly
    4. Test full workflow (Architect → Factory → Editor's Desk → Feedback)

### Phase 6: Testing & Validation ⏳ PENDING

- [ ] **Functionality Tests**
  - [ ] Homepage (Handshake) loads with authentication
  - [ ] Architect's Table accepts product input
  - [ ] Factory Floor generates content (CrewAI agents)
  - [ ] Editor's Desk displays generated content
  - [ ] Feedback system saves to Supabase
  - [ ] Feedback Guide page accessible
  - [ ] ChromaDB rebuilds from Data/ files on startup

- [ ] **Data Persistence Tests**
  - [ ] Submit feedback → verify in Supabase dashboard
  - [ ] Restart app → verify feedback persists
  - [ ] Check feedback retrieval works

- [ ] **Performance Tests**
  - [ ] CrewAI agents execute successfully
  - [ ] Hebrew text renders correctly (RTL)
  - [ ] ChromaDB vector search works
  - [ ] No timeout errors on content generation

---

## 🔧 Key Technical Decisions

### 1. **Dual Backend Strategy**
- **Local**: SQLite database (feedback/feedback.db)
- **Cloud**: Supabase PostgreSQL
- **Detection**: Automatic via `is_streamlit_cloud()` in config.py

### 2. **Ephemeral Filesystem Handling**
- **Outputs**: `/tmp/outputs` (regenerated each session)
- **ChromaDB**: `/tmp/.chromadb` (rebuilt from Data/ files)
- **Data files**: Permanent (checked into git)

### 3. **Python Version**
- **Local dev**: Python 3.11
- **Cloud**: Python 3.11 (via .python-version file)

### 4. **Supabase Schema**
- **Matched to SQLite**: Exact same column names and types
- **CSV import friendly**: Direct mapping without transformation
- **RLS enabled**: Row Level Security for production readiness

---

## 📁 Important Files

| File | Purpose | Status |
|------|---------|--------|
| requirements.txt | Python dependencies | ✅ Updated |
| .python-version | Python version spec | ✅ Created |
| .streamlit/config.toml | Streamlit settings | ✅ Created |
| .streamlit/secrets.toml.example | Secrets template | ✅ Created |
| config.py | Environment detection | ✅ Modified |
| core/feedback_manager.py | Supabase integration | ✅ Modified |
| supabase_schema_correct.sql | Database schema | ✅ Created |
| feedback_export.csv | Backup of 43 entries | ✅ Exported |
| export_feedback_to_csv.py | Export script | ✅ Created |

---

## 🚨 Known Issues & Resolutions

### Issue 1: Requirements Installation Error ✅ RESOLVED
- **Problem**: Exact version pins (==) failed on Python 3.13
- **Solution**: Changed to flexible versions (>=)
- **Commit**: 2fef7e3

### Issue 2: Sidebar Menu Text Invisible ✅ RESOLVED
- **Problem**: Black text on black background
- **Solution**: Added explicit CSS color rules for sidebar navigation
- **Commit**: ccf2123

### Issue 3: Content Area Too Narrow ✅ RESOLVED
- **Problem**: Layout set to "centered" (narrow width)
- **Solution**: Changed to "wide" layout in app.py
- **Commit**: deac866

### Issue 4: Schema Mismatch ⏳ IN PROGRESS
- **Problem**: Initial Supabase schema didn't match SQLite
- **Solution**: Created supabase_schema_correct.sql with exact schema
- **Status**: Waiting for user to run SQL

---

## 🎯 Next Immediate Actions

1. **Run SQL Schema** in Supabase SQL Editor
   - File: supabase_schema_correct.sql
   - Confirm destructive operation warning
   - Creates correct table structure

2. **Import CSV** to Supabase
   - File: feedback_export.csv
   - Location: Table Editor → feedback → Insert → Import CSV
   - Restores 43 existing feedback entries

3. **Reboot App** in Streamlit Cloud
   - Verify feedback saves to Supabase
   - Test full workflow end-to-end

---

## 📊 Deployment Timeline

| Phase | Started | Completed | Duration |
|-------|---------|-----------|----------|
| Pre-Deployment Prep | 2025-12-29 | ✅ | ~30 min |
| Supabase Integration | 2025-12-29 | ✅ (code) | ~20 min |
| Git Operations | 2025-12-29 | ✅ | ~10 min |
| Supabase DB Setup | 2025-12-29 | ⏳ | In progress |
| Streamlit Cloud Deploy | 2025-12-29 | 🟡 Partial | In progress |
| Testing & Validation | - | ⏳ | Pending |

---

## 🔗 Important URLs

- **GitHub Repo**: https://github.com/ShaharSGA/Project
- **Streamlit App**: [URL provided after deployment]
- **Supabase Dashboard**: https://app.supabase.com (Project: jszdmgcdofxz1iddvgpb)

---

## 📝 Post-Deployment Notes

### Limitations (By Design)
1. **ChromaDB rebuilds on restart**: Expected behavior (vector DB from Data/ files)
2. **Outputs ephemeral**: Generated content not persisted (by design)
3. **Single client pilot**: Lierac only (expand later)

### Future Enhancements (Not in Scope)
- [ ] Full CRUD migration to Supabase for all feedback operations
- [ ] Multi-client support beyond Lierac
- [ ] Persistent output storage
- [ ] User authentication beyond access code

---

**END OF DEPLOYMENT PLAN**
