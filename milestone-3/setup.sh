#!/usr/bin/env bash
#
# CS348 Project - Complete Setup Script
# This script sets up the database, loads data, and runs the Flask application
#
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Database configuration
DB_NAME="coop_salaries"
DB_USER="$(whoami)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CS348 Waterloo Co-op Salaries Explorer${NC}"
echo -e "${BLUE}Complete Setup Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Get MySQL credentials
echo -e "${YELLOW}Step 1: MySQL Authentication${NC}"
echo "How do you connect to MySQL?"
echo "1) sudo mysql (no password)"
echo "2) mysql -u $DB_USER -p (with password)"
echo "3) mysql -u root -p (as root with password)"
read -p "Enter choice [1-3]: " MYSQL_CHOICE

case $MYSQL_CHOICE in
    1)
        echo -e "${GREEN}Will use 'sudo mysql' for database operations${NC}"
        USE_SUDO="yes"
        DB_USER="root"
        DB_PASS=""
        ;;
    2)
        echo "Enter your MySQL password for user '$DB_USER':"
        read -rs DB_PASS
        USE_SUDO="no"
        ;;
    3)
        DB_USER="root"
        echo "Enter your MySQL root password:"
        read -rs DB_PASS
        USE_SUDO="no"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
echo ""

# Step 2: Create database
echo -e "${YELLOW}Step 2: Creating database '$DB_NAME'...${NC}"
if [ "$USE_SUDO" = "yes" ]; then
    sudo mysql -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;"
elif [ -z "$DB_PASS" ]; then
    mysql -u "$DB_USER" -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;"
else
    mysql -u "$DB_USER" -p"$DB_PASS" -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;" 2>&1 | grep -v "Using a password"
fi
echo -e "${GREEN}✓ Database '$DB_NAME' created successfully!${NC}"
echo ""

# Step 3: Create tables
echo -e "${YELLOW}Step 3: Creating database schema...${NC}"
if [ ! -f "create-tables.sql" ]; then
    echo -e "${RED}Error: create-tables.sql not found in current directory${NC}"
    exit 1
fi

if [ "$USE_SUDO" = "yes" ]; then
    sudo mysql "$DB_NAME" < create-tables.sql
elif [ -z "$DB_PASS" ]; then
    mysql -u "$DB_USER" "$DB_NAME" < create-tables.sql
else
    mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < create-tables.sql 2>&1 | grep -v "Using a password"
fi
echo -e "${GREEN}✓ Database schema created successfully!${NC}"
echo ""

# Step 4: Load sample data
echo -e "${YELLOW}Step 4: Loading sample data...${NC}"
if [ -f "test-sample.sql" ]; then
    if [ "$USE_SUDO" = "yes" ]; then
        sudo mysql "$DB_NAME" < test-sample.sql
    elif [ -z "$DB_PASS" ]; then
        mysql -u "$DB_USER" "$DB_NAME" < test-sample.sql
    else
        mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < test-sample.sql 2>&1 | grep -v "Using a password"
    fi
    echo -e "${GREEN}✓ Sample data loaded successfully!${NC}"
else
    echo -e "${YELLOW}⚠ test-sample.sql not found, skipping sample data${NC}"
fi
echo ""

# Step 5: Verify database
echo -e "${YELLOW}Step 5: Verifying database setup...${NC}"
if [ "$USE_SUDO" = "yes" ]; then
    EMPLOYER_COUNT=$(sudo mysql "$DB_NAME" -se "SELECT COUNT(*) FROM Employer;" 2>/dev/null || echo "0")
elif [ -z "$DB_PASS" ]; then
    EMPLOYER_COUNT=$(mysql -u "$DB_USER" "$DB_NAME" -se "SELECT COUNT(*) FROM Employer;" 2>/dev/null || echo "0")
else
    EMPLOYER_COUNT=$(mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -se "SELECT COUNT(*) FROM Employer;" 2>&1 | grep -v "Using a password" | tail -1)
fi
echo -e "${GREEN}✓ Database verified: $EMPLOYER_COUNT employers found${NC}"
echo ""

# Step 6: Navigate to app directory
echo -e "${YELLOW}Step 6: Navigating to app directory...${NC}"
if [ ! -d "app" ]; then
    echo -e "${RED}Error: app directory not found${NC}"
    exit 1
fi

cd app
echo -e "${GREEN}✓ Changed to app directory${NC}"
echo ""

# Step 7: Set up Python virtual environment
echo -e "${YELLOW}Step 7: Setting up Python virtual environment...${NC}"

# Check if python3-venv is available
if ! python3 -m venv --help &> /dev/null; then
    echo -e "${RED}Error: python3-venv is not installed${NC}"
    echo -e "${YELLOW}Install it with: sudo apt install python3-venv${NC}"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
if [ ! -f "venv/bin/activate" ]; then
    echo -e "${RED}Error: venv/bin/activate not found${NC}"
    echo -e "${YELLOW}Try removing the venv directory and running again: rm -rf app/venv${NC}"
    exit 1
fi

source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Step 8: Install Python dependencies
echo -e "${YELLOW}Step 8: Installing Python dependencies...${NC}"
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: requirements.txt not found in app directory${NC}"
    exit 1
fi

pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

# Step 9: Create .env file in app directory
echo -e "${YELLOW}Step 9: Creating environment configuration...${NC}"
if [ ! -f ".env" ]; then
    # Adjust credentials for Flask app based on authentication method
    if [ "$USE_SUDO" = "yes" ]; then
        # For sudo mysql, we need to create a proper MySQL user for the app
        echo -e "${YELLOW}Creating MySQL user for Flask application...${NC}"
        APP_USER="flask_user"
        APP_PASS="flask_password_$(date +%s)"
        
        sudo mysql -e "CREATE USER IF NOT EXISTS '${APP_USER}'@'localhost' IDENTIFIED BY '${APP_PASS}';"
        sudo mysql -e "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${APP_USER}'@'localhost';"
        sudo mysql -e "FLUSH PRIVILEGES;"
        
        echo -e "${GREEN}✓ MySQL user '${APP_USER}' created for Flask app${NC}"
        
        cat > .env << EOF
DB_HOST=127.0.0.1
DB_USER=${APP_USER}
DB_PASS=${APP_PASS}
DB_NAME=${DB_NAME}
FLASK_ENV=development
FLASK_DEBUG=1
EOF
    else
        # Use the credentials provided
        cat > .env << EOF
DB_HOST=127.0.0.1
DB_USER=${DB_USER}
DB_PASS=${DB_PASS}
DB_NAME=${DB_NAME}
FLASK_ENV=development
FLASK_DEBUG=1
EOF
    fi
    echo -e "${GREEN}✓ Environment file created (app/.env)${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists in app/, skipping creation${NC}"
    echo -e "${YELLOW}  Please verify your database credentials in app/.env${NC}"
    echo -e "${YELLOW}  If you're having connection issues, delete app/.env and run this script again${NC}"
fi
echo ""

# Step 10: Run the application
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Starting Flask application...${NC}"
echo -e "${GREEN}Access the application at: http://127.0.0.1:5000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo -e "${RED}Error: app.py not found in app directory${NC}"
    exit 1
fi

# Run the Flask app
python3 app.py