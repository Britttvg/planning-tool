# Private Data Submodule Setup

Follow these steps to set up a private data repository:

## 1. Create Private Repository
1. Go to GitHub and create a new **private** repository named `planning-tool-data`
2. Initialize it with a README

## 2. Move Data to Private Repository

```bash
# Clone the private repository
cd /tmp
git clone https://github.com/Britttvg/planning-tool-data.git
cd planning-tool-data

# Copy your data files
cp ~/Apps/Hobby/planning-tool/src/data/* .

# Add and commit
git add .
git commit -m "Initial data files"
git push origin main
```

## 3. Add as Submodule

```bash
# In your main project directory
cd ~/Apps/Hobby/planning-tool

# Remove data from Git tracking (but keep local file)
git rm --cached src/data/data_planning_dev.csv
git commit -m "Remove data from main repo"

# Add the private repo as a submodule
git submodule add https://github.com/Britttvg/planning-tool-data.git private-data

# Commit the submodule
git add .gitmodules private-data
git commit -m "Add private data submodule"
git push
```

## 4. For Other Users/Deployments

When cloning the repository:
```bash
git clone --recurse-submodules https://github.com/Britttvg/planning-tool.git
```

Or if already cloned:
```bash
git submodule init
git submodule update
```

## 5. Update Data

To update data in the private repository:
```bash
cd private-data
# Make your changes to the CSV files
git add .
git commit -m "Update planning data"
git push

cd ..
# Update the submodule reference in main repo
git add private-data
git commit -m "Update data submodule reference"
git push
```

## Notes
- The private repository `planning-tool-data` will contain your sensitive CSV files
- Only people with access to the private repo can see the data
- The main public repo only contains a reference to a specific commit in the private repo
- Both repositories need to be updated when data changes