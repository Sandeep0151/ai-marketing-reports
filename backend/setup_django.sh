#!/bin/bash
# setup_django.sh - Complete Django backend setup script

echo "🚀 Setting up Django Backend for AI Marketing Reports"
echo "=================================================="

# Step 1: Activate virtual environment
echo "📁 Activating virtual environment..."
source venv/bin/activate

# Step 2: Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Step 3: Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << 'EOF'
# Django Settings
SECRET_KEY=django-insecure-your-secret-key-change-in-production-$(date +%s)
DEBUG=True

# Database Configuration (using SQLite for development)
DB_NAME=marketing_reports.db
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# API Keys (add your keys here)
OPENAI_API_KEY=
GOOGLE_API_KEY=
SEMRUSH_API_KEY=
SERPAPI_KEY=

# Social Media APIs
FACEBOOK_ACCESS_TOKEN=
TWITTER_BEARER_TOKEN=
LINKEDIN_ACCESS_TOKEN=

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Frontend URL (for email notifications)
FRONTEND_URL=http://localhost:3000
EOF
    echo "✅ Created .env file. Please add your API keys!"
else
    echo "⚠️ .env file already exists, skipping creation."
fi

# Step 4: Run database migrations
echo "🗄️ Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Step 5: Create superuser
echo "👤 Creating admin user..."
echo "Please create an admin user for the Django admin panel:"
python manage.py createsuperuser

# Step 6: Create sample data
echo "📊 Creating sample report templates..."
python manage.py create_sample_data

# Step 7: Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Django backend setup completed!"
echo ""
echo "🎯 Next steps:"
echo "1. Add your API keys to the .env file"
echo "2. Start Redis: redis-server"
echo "3. Start Django: python manage.py runserver"
echo "4. Start Celery: celery -A config worker -l info"
echo "5. Access admin at: http://localhost:8000/admin"
echo ""
echo "🔑 API Keys you'll need:"
echo "- OpenAI API Key: https://platform.openai.com/api-keys"
echo "- Google API Key: https://console.developers.google.com/"
echo "- Optional: SEMrush API, SerpAPI for advanced features"
echo ""

# Test Django setup
echo "🧪 Testing Django setup..."
python manage.py check

if [ $? -eq 0 ]; then
    echo "✅ Django setup validation passed!"
else
    echo "❌ Django setup validation failed. Please check the errors above."
    exit 1
fi

# Test database connection
echo "🧪 Testing database connection..."
python manage.py shell -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Database connection successful!')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

# Create a test report (optional)
echo ""
echo "🧪 Would you like to create a test report? (y/n)"
read -r create_test

if [ "$create_test" = "y" ]; then
    echo "🔄 Creating test report..."
    python manage.py shell -c "
from reports.models import Website, Report
from reports.tasks import generate_marketing_report

# Create test website
website, created = Website.objects.get_or_create(
    domain='example.com',
    defaults={
        'url': 'https://example.com',
        'company_name': 'Example Company'
    }
)

# Create test report
report = Report.objects.create(
    website=website,
    report_type='basic',
    requester_email='test@example.com'
)

print(f'✅ Test report created with ID: {report.id}')
print(f'📊 Check it at: http://localhost:8000/admin/reports/report/{report.id}/change/')

# Start report generation (if Celery is running)
try:
    generate_marketing_report.delay(str(report.id))
    print('🚀 Report generation started!')
except Exception as e:
    print(f'⚠️ Could not start report generation (Celery may not be running): {e}')
"
fi

echo ""
echo "🎉 Setup complete! Your Django backend is ready."

# Start services (optional)
echo ""
echo "🚀 Would you like to start the development servers now? (y/n)"
read -r start_servers

if [ "$start_servers" = "y" ]; then
    echo "Starting development servers..."

    # Check if Redis is running
    if ! pgrep redis-server > /dev/null; then
        echo "⚠️ Redis is not running. Starting Redis..."
        redis-server --daemonize yes
    fi

    # Start Django in background
    echo "🌐 Starting Django server..."
    python manage.py runserver &
    DJANGO_PID=$!

    # Start Celery in background
    echo "⚙️ Starting Celery worker..."
    celery -A config worker -l info &
    CELERY_PID=$!

    echo ""
    echo "✅ Servers started!"
    echo "🌐 Django: http://localhost:8000"
    echo "👨‍💼 Admin: http://localhost:8000/admin"
    echo "📊 API: http://localhost:8000/api/"
    echo ""
    echo "Press Ctrl+C to stop all servers"

    # Wait for interrupt
    trap "echo ''; echo '🛑 Stopping servers...'; kill $DJANGO_PID $CELERY_PID; exit" INT
    wait
fi

# Additional setup for development
cat > start_dev.sh << 'EOF'
#!/bin/bash
# start_dev.sh - Start all development services

echo "🚀 Starting AI Marketing Reports Development Environment"

# Activate virtual environment
source venv/bin/activate

# Start Redis if not running
if ! pgrep redis-server > /dev/null; then
    echo "📦 Starting Redis..."
    redis-server --daemonize yes
fi

# Start Django
echo "🌐 Starting Django server..."
python manage.py runserver &
DJANGO_PID=$!

# Start Celery worker
echo "⚙️ Starting Celery worker..."
celery -A config worker -l info &
CELERY_PID=$!

# Start Celery beat (for scheduled tasks)
echo "⏰ Starting Celery beat..."
celery -A config beat -l info &
BEAT_PID=$!

echo ""
echo "✅ All services started!"
echo "🌐 Django: http://localhost:8000"
echo "👨‍💼 Admin: http://localhost:8000/admin"
echo "📊 API Docs: http://localhost:8000/api/"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $DJANGO_PID $CELERY_PID $BEAT_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Wait for services
wait
EOF

chmod +x start_dev.sh

echo ""
echo "📝 Created start_dev.sh script for easy development server startup"
echo "📝 Run './start_dev.sh' to start all services at once"

# Create test API endpoints script
cat > test_api.py << 'EOF'
#!/usr/bin/env python
"""
Test script for API endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_website_validation():
    """Test website URL validation"""
    print("🧪 Testing website URL validation...")

    url = f"{BASE_URL}/reports/validate-url/"
    data = {"url": "https://example.com"}

    try:
        response = requests.post(url, json=data)
        print(f"✅ Status: {response.status_code}")
        print(f"📝 Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_report_creation():
    """Test report creation"""
    print("\n🧪 Testing report creation...")

    url = f"{BASE_URL}/reports/create/"
    data = {
        "website_url": "https://example.com",
        "report_type": "basic",
        "requester_email": "test@example.com",
        "requester_name": "Test User"
    }

    try:
        response = requests.post(url, json=data)
        print(f"✅ Status: {response.status_code}")
        result = response.json()
        print(f"📝 Report ID: {result.get('id')}")
        return result.get('id')
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_report_status(report_id):
    """Test report status"""
    if not report_id:
        return

    print(f"\n🧪 Testing report status for {report_id}...")

    url = f"{BASE_URL}/reports/{report_id}/"

    try:
        response = requests.get(url)
        print(f"✅ Status: {response.status_code}")
        result = response.json()
        print(f"📊 Report Status: {result.get('status')}")
        print(f"📈 Progress: {result.get('progress_percentage', 0)}%")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_website_analysis():
    """Test direct website analysis"""
    print("\n🧪 Testing direct website analysis...")

    url = f"{BASE_URL}/data-collectors/analyze-website/"
    data = {"url": "https://example.com"}

    try:
        response = requests.post(url, json=data)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"📝 Title: {result.get('title', 'N/A')}")
            print(f"📝 Word Count: {result.get('word_count', 0)}")
            print(f"📝 Has SSL: {result.get('has_ssl', False)}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🚀 Testing AI Marketing Reports API")
    print("=" * 40)

    # Test basic endpoints
    test_website_validation()
    test_website_analysis()

    # Test report creation and monitoring
    report_id = test_report_creation()
    time.sleep(2)  # Wait a bit
    test_report_status(report_id)

    print("\n✅ API testing completed!")
    print("🌐 Check Django admin for more details: http://localhost:8000/admin")

if __name__ == "__main__":
    main()
EOF

chmod +x test_api.py

echo "📝 Created test_api.py script for testing API endpoints"
echo "📝 Run 'python test_api.py' to test the API"

echo ""
echo "🎉 Django backend setup is complete!"
echo ""
echo "📚 What you have now:"
echo "✅ Complete Django backend with REST API"
echo "✅ Celery task queue for background processing"
echo "✅ WebSocket support for real-time updates"
echo "✅ AI-powered analysis with OpenAI integration"
echo "✅ Comprehensive data collection framework"
echo "✅ Admin interface for management"
echo "✅ Development scripts and testing tools"
echo ""
echo "🔧 Ready for Next.js frontend integration!"