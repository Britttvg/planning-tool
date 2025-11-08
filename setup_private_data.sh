#!/bin/bash

# Setup script for private data submodule
# Run this script after creating your private repository on GitHub

echo "🔧 Setting up private data submodule..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this script from the planning-tool directory"
    exit 1
fi

# Check if private-data directory already exists
if [ -d "private-data" ]; then
    echo "⚠️ private-data directory already exists. Skipping submodule setup."
else
    # Add the private repository as a submodule
    echo "📁 Adding private repository as submodule..."
    git submodule add https://github.com/Britttvg/planning-tool-data.git private-data
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to add submodule. Make sure the private repository exists and is accessible."
        exit 1
    fi
fi

# Copy existing data if it exists
if [ -f "src/data/data_planning_dev.csv" ] && [ ! -f "private-data/data_planning_dev.csv" ]; then
    echo "📋 Copying existing data to private repository..."
    cp src/data/data_planning_dev.csv private-data/
    
    # Commit to private repository
    cd private-data
    git add data_planning_dev.csv
    git commit -m "Add initial planning data"
    git push
    cd ..
fi

# Remove data from main repository tracking
if git ls-files --error-unmatch src/data/data_planning_dev.csv > /dev/null 2>&1; then
    echo "🗑️ Removing data from main repository tracking..."
    git rm --cached src/data/data_planning_dev.csv
    git add .gitmodules private-data
    git commit -m "Move data to private submodule and remove from main repo"
else
    echo "📝 Committing submodule configuration..."
    git add .gitmodules private-data
    git commit -m "Add private data submodule"
fi

echo "✅ Setup complete!"
echo ""
echo "📌 Next steps:"
echo "1. Push changes to your main repository: git push"
echo "2. Other users should clone with: git clone --recurse-submodules [repo-url]"
echo "3. Or initialize submodules: git submodule init && git submodule update"