# Neeget - Service Marketplace Platform

A comprehensive web application for connecting service providers with customers, built with Flask and featuring a responsive frontend.

## 🚀 Features

### Core Functionality
- **User Management**: Registration, login, profile management with role-based access
- **Service Marketplace**: Browse, search, and filter services by category and location
- **Booking System**: Complete booking workflow from request to completion
- **Payment Integration**: Payment tracking with platform fee calculation
- **Real-time Chat**: Messaging system between users and providers
- **Review System**: Rating and feedback functionality
- **Admin Dashboard**: Comprehensive admin panel with analytics and user management

### User Roles
1. **Regular Users**: Browse and book services, manage bookings, leave reviews
2. **Service Providers**: Manage services, handle booking requests, communicate with customers
3. **Administrators**: Platform management, user oversight, analytics, fraud monitoring

## 🛠 Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: JSON file-based storage with custom DataManager
- **Authentication**: bcrypt password hashing with session management
- **Security**: CSRF protection, input validation, role-based access control
- **Forms**: Flask-WTF for form handling and validation

### Frontend
- **Framework**: HTML5, CSS3, JavaScript
- **Styling**: Bootstrap 4.5.2 for responsive design
- **Icons**: Font Awesome 5.15.4
- **Design**: Custom CSS with modern animations and gradients

## 📁 Project Structure

```
Neeget/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── data_manager.py       # JSON database management
├── models.py             # Data models and schemas
├── forms.py              # WTForms for validation
├── auth.py               # Authentication blueprint
├── services.py           # Service management blueprint
├── bookings.py           # Booking system blueprint
├── chat.py               # Messaging system blueprint
├── admin.py              # Admin panel blueprint
├── profile.py            # Profile management blueprint
├── data/                 # JSON database files
│   ├── Users.json
│   ├── Services.json
│   ├── Service_Categories.json
│   ├── Bookings.json
│   ├── Payments.json
│   ├── Chat_Messages.json
│   ├── Reviews.json
│   ├── Notifications.json
│   ├── Support_Tickets.json
│   └── Platform_Metrics.json
├── templates/            # HTML templates
│   ├── auth/            # Authentication pages
│   ├── services/        # Service-related pages
│   ├── bookings/        # Booking management pages
│   ├── chat/            # Chat interface
│   ├── admin/           # Admin panel pages
│   └── profile/         # Profile management pages
├── static/              # Static assets
│   └── css/
│       └── style.css    # Custom styling
└── README.md           # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- pip (Python package manager)

### Installation Steps

1. **Clone or extract the project**
   ```bash
   cd Neeget
   ```

2. **Install required packages**
   ```bash
   pip3 install flask flask-wtf bcrypt
   ```

3. **Run the application**
   ```bash
   python3.11 app.py
   ```

4. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## 👥 Default User Accounts

### Administrator
- **Email**: `admin@neeget.com`
- **Password**: `password`
- **Role**: Admin (full platform access)

### Sample Users
- **User**: `john@example.com` / `password` (Regular user)
- **Provider**: `alice@example.com` / `password` (Service provider - House Cleaner)
- **Provider**: `bob@example.com` / `password` (Service provider - Plumber)

## 🎯 Key Features Explained

### 1. Service Management
- **Browse Services**: Filter by category, location, and price range
- **Service Details**: Comprehensive service information with provider details
- **Provider Profiles**: Professional information, expertise, and portfolio links

### 2. Booking System
- **Request Booking**: Users can request services with preferred dates
- **Provider Response**: Providers can accept/reject booking requests
- **Status Tracking**: Real-time booking status updates
- **Payment Processing**: Automatic fee calculation with platform commission

### 3. Communication
- **In-app Chat**: Real-time messaging between users and providers
- **Notifications**: System notifications for all important events
- **Email Integration**: Ready for email notification implementation

### 4. Admin Features
- **User Management**: Suspend, ban, activate, and verify users
- **Analytics Dashboard**: Platform metrics and service popularity
- **Support System**: Ticket management and resolution
- **Fraud Monitoring**: Automated detection of suspicious activities

### 5. Security Features
- **Password Hashing**: bcrypt for secure password storage
- **CSRF Protection**: Form security against cross-site attacks
- **Input Validation**: Comprehensive data validation and sanitization
- **Role-based Access**: Secure access control for different user types

## 🔧 Configuration

### Database Configuration
The application uses JSON files for data storage. Configuration can be modified in `config.py`:

```python
class Config:
    SECRET_KEY = 'your-secret-key-here'
    JSON_DATABASE_DIR = 'data'
```

### Adding New Service Categories
1. Edit `data/Service_Categories.json`
2. Add new category with unique ID and name
3. Restart the application

## 📊 Data Models

### Users
- ID, name, email, contact, NID, password hash
- Role (user/service_provider/admin)
- Verification status, professional details

### Services
- ID, category, provider, name, description, price, location

### Bookings
- ID, user, provider, service, dates, status, payment method

### Reviews
- ID, booking, user, provider, rating, comment, date

## 🚀 Deployment

### Development
The application runs in debug mode by default for development.

### Production Considerations
1. **Change Secret Key**: Use a secure random secret key
2. **Database**: Consider migrating to PostgreSQL or MySQL for production
3. **Web Server**: Use Gunicorn or uWSGI with Nginx
4. **SSL**: Implement HTTPS for secure communication
5. **Environment Variables**: Use environment variables for sensitive configuration

## 🔮 Future Enhancements

### Planned Features
- **Real-time Notifications**: WebSocket implementation
- **Payment Gateway**: Stripe/PayPal integration
- **Mobile App**: React Native mobile application
- **Advanced Search**: Elasticsearch integration
- **File Uploads**: Profile pictures and service images
- **Email System**: Automated email notifications
- **API**: RESTful API for mobile app integration

### Technical Improvements
- **Database Migration**: Move to relational database
- **Caching**: Redis for session and data caching
- **Testing**: Comprehensive unit and integration tests
- **CI/CD**: Automated deployment pipeline
- **Monitoring**: Application performance monitoring

## 🐛 Known Issues

1. **Browser Timeout**: Some browser testing experienced timeout issues (application runs correctly)
2. **File Upload**: Image upload functionality not yet implemented
3. **Email**: Email notifications require SMTP configuration

## 📝 API Documentation

### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout

### Service Endpoints
- `GET /services/browse` - Browse all services
- `GET /services/<id>` - Get service details
- `POST /services/add` - Add new service (providers only)

### Booking Endpoints
- `GET /bookings/` - List user bookings
- `POST /bookings/book/<service_id>` - Create booking
- `POST /bookings/<id>/accept` - Accept booking (providers)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is developed for educational and demonstration purposes.

## 📞 Support

For support and questions:
- Create a support ticket through the application
- Contact the development team
- Check the documentation for common issues

---

**Neeget Platform** - Connecting service providers with customers efficiently and securely.

