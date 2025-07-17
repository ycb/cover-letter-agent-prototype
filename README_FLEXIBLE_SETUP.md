# 🚀 Flexible Drive Configuration System

This system is designed to work for **any user** with **any folder structure**. No more hardcoded file names or folder IDs!

## 🎯 Key Features

### ✅ **Auto-Discovery**
- Finds files by name patterns (e.g., "resume grid", "job tracker", "star stories")
- Works with any naming convention
- Multiple fallback strategies

### ✅ **Flexible Parsing**
- Adapts to different spreadsheet layouts
- Handles various column arrangements
- Pattern-based content detection

### ✅ **CLI Configuration**
- Interactive setup wizard
- User-specific configurations
- Easy to use for non-technical users

## 📋 How It Works

### 1. **File Discovery Strategies**

The system tries multiple strategies to find your files:

```yaml
# Strategy 1: Direct file ID (if you know it)
materials:
  star_stories: "your-file-id-here"

# Strategy 2: Pattern matching in folders
file_discovery:
  star_stories_patterns:
    - "resume grid"
    - "star stories" 
    - "behavioral examples"
    - "situation action result"
    - "STAR"

# Strategy 3: Fallback folders
fallback_folders:
  star_stories: "your-folder-id-here"
```

### 2. **Flexible Spreadsheet Parsing**

Handles different spreadsheet layouts automatically:

```yaml
spreadsheet_parsing:
  star_stories:
    column_layouts:
      - ["title", "situation", "action", "result"]
      - ["company", "situation", "action", "result"] 
      - ["role", "situation", "action", "result"]
      - ["project", "situation", "action", "result"]
    title_patterns:
      - "enact"
      - "meta"
      - "salesforce"
      - "samsung"
```

## 🛠️ Usage Examples

### **For Any User - Setup**

```bash
# 1. List available users
python scripts/run_analysis.py --list-users

# 2. Run interactive setup for new user
python scripts/run_analysis.py --configure

# 3. Run analysis for specific user
python scripts/run_analysis.py --user jane
```

### **Example: Jane's Setup**

Jane has a different folder structure:
- Her STAR stories are in "My Career Stories.xlsx"
- Job tracker is "Applications 2024.xlsx" 
- Cover letters in "Job Applications" folder

The system will automatically find these files using pattern matching!

### **Example: Bob's Setup**

Bob uses different naming:
- "Behavioral Examples.xlsx" for STAR stories
- "Job Search Tracker.xlsx" for applications
- "Portfolio Work" folder for projects

The system adapts to his naming conventions.

## 🔧 Configuration Examples

### **Minimal Configuration**
```yaml
google_drive:
  materials:
    star_stories: "folder-id-here"  # Just point to folder
  file_discovery:
    star_stories_patterns:
      - "resume grid"
      - "star stories"
```

### **Advanced Configuration**
```yaml
google_drive:
  materials:
    star_stories: "specific-file-id"
  file_discovery:
    star_stories_patterns:
      - "resume grid"
      - "star stories"
      - "behavioral examples"
      - "situation action result"
      - "STAR"
    fallback_folders:
      star_stories: "backup-folder-id"
  spreadsheet_parsing:
    star_stories:
      column_layouts:
        - ["title", "situation", "action", "result"]
        - ["company", "situation", "action", "result"]
      title_patterns:
        - "enact"
        - "meta"
        - "salesforce"
```

## 🎯 Benefits

### **For Users:**
- ✅ No need to rename files
- ✅ Works with existing folder structure
- ✅ Interactive setup wizard
- ✅ Multiple fallback strategies

### **For Developers:**
- ✅ No hardcoded file names
- ✅ Configurable patterns
- ✅ Extensible architecture
- ✅ Easy to add new file types

## 🚀 Future Enhancements

### **UI Version (Coming Soon)**
```python
# Future: Web-based configuration
python scripts/web_config.py --port 8080
```

### **Auto-Learning**
```python
# Future: Learn from user behavior
python scripts/run_analysis.py --learn-patterns
```

### **Template System**
```python
# Future: Pre-built templates
python scripts/run_analysis.py --template "product-manager"
```

## 📊 Success Metrics

The system successfully handles:
- ✅ Different file naming conventions
- ✅ Various folder structures  
- ✅ Multiple spreadsheet layouts
- ✅ Missing or moved files (with fallbacks)
- ✅ New users with zero configuration

## 🔄 Migration from Hardcoded

**Before (Hardcoded):**
```python
# Only works for Peter's setup
resume_grid_id = "16zJzR_XVZtdtuQfacZXRZm9yHHyKNWkp6YTeueI085E"
```

**After (Flexible):**
```python
# Works for any user
file_id = find_star_stories_file(drive, config)
```

This makes the system truly universal and user-friendly! 🎉 