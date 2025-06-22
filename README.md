# Hostel Management System

## 🏢 Overview

A comprehensive web-based hostel management system built with Flask, designed to streamline hostel operations for both administrators and students. The system provides separate portals for administrators and students, featuring room management, booking systems, payment tracking, and real-time analytics.

## ✨ Features

### 🔐 Authentication & Security
- **Role-based Access Control**: Separate admin and student portals
- **Secure Authentication**: Password hashing with Werkzeug
- **Session Management**: Secure session handling with automatic logout
- **Input Validation**: Server-side validation for all forms

### 👨‍💼 Admin Portal
- **Dashboard Analytics**: Real-time statistics with interactive charts
- **Student Management**: Complete CRUD operations for student records
- **Room Management**: Add, edit, and delete rooms with amenities
- **Booking Management**: Approve/reject booking requests
- **Payment Tracking**: Monitor payments and financial reports
- **Advanced Filtering**: Search and filter functionality across all modules

### 🎓 Student Portal
- **Room Browser**: Interactive interface to browse available rooms
- **Advanced Search**: Filter rooms by type, price, and amenities
- **Booking System**: Submit booking requests with date selection
- **Personal Dashboard**: View current booking status and details
- **Responsive Design**: Mobile-friendly interface

## 🛠 Technology Stack

- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: MySQL with PyMySQL driver
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Custom CSS with Font Awesome icons
- **Charts**: Chart.js for data visualization
- **Authentication**: Werkzeug password hashing
- **Database ORM**: Flask-SQLAlchemy

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **MySQL**: 8.0 or higher
- **Operating System**: Windows, macOS, or Linux

### Python Dependencies
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
PyMySQL==1.1.0
cryptography==41.0.4
Werkzeug==2.3.7
```

## 🚀 Installation & Setup

### 1. Prerequisites
```bash
# Install MySQL (macOS with Homebrew)
brew install mysql
brew services start mysql

# Create database
mysql -u root -p
CREATE DATABASE hostel_managementV2;
EXIT;
```

### 2. Application Setup
```bash
# Clone the repository
git clone https://github.com/FarisMD22/TSE-Project---HMS.git
cd hostel-management-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure database (update credentials in app.py if needed)
# Default: mysql+pymysql://root:password@localhost/hostel_managementV2

# Run the application
python app.py
```

### 3. Initial Setup
The application will automatically:
- Create all database tables
- Insert sample room data
- Create default admin account

## 🔑 Default Login Credentials

### Administrator Access
- **Email**: `admin@hostel.com`
- **Password**: `admin123`

### Student Access
Students must register their own accounts using the registration form.

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'student') NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Rooms Table
```sql
CREATE TABLE rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(10) UNIQUE NOT NULL,
    room_type ENUM('single', 'double', 'triple', 'quad') NOT NULL,
    capacity INT NOT NULL,
    rent_per_month DECIMAL(10,2) NOT NULL,
    amenities TEXT,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Bookings Table
```sql
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    room_id INT,
    start_date DATE NOT NULL,
    end_date DATE,
    status ENUM('pending', 'approved', 'rejected', 'active', 'completed') DEFAULT 'pending',
    total_amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
);
```

### Payments Table
```sql
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT,
    amount DECIMAL(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method ENUM('cash', 'online', 'card') DEFAULT 'cash',
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);
```

## 🌐 API Endpoints

### Authentication
- `POST /login` - User authentication
- `POST /register` - Student registration
- `GET /logout` - User logout

### Admin Endpoints
- `GET /admin/dashboard` - Admin dashboard with statistics
- `GET /admin/students` - List all students
- `GET /admin/rooms` - Room management interface
- `GET /admin/bookings` - Booking management interface
- `GET /admin/payments` - Payment tracking interface

### Room Management (Admin Only)
- `POST /api/rooms/add` - Add new room
- `PUT /api/rooms/<id>/update` - Update room details
- `DELETE /api/rooms/<id>/delete` - Delete room

### Booking Management
- `POST /api/bookings/request` - Submit booking request (Student)
- `POST /api/bookings/<id>/approve` - Approve booking (Admin)
- `POST /api/bookings/<id>/reject` - Reject booking (Admin)

### Analytics
- `GET /api/dashboard/stats` - Dashboard statistics (Admin)

## 🎨 User Interface Features

### Design Principles
- **Mobile-First**: Responsive design optimized for all devices
- **Accessibility**: WCAG 2.1 AA compliance with keyboard navigation
- **Modern UI**: Clean, intuitive interface with consistent styling
- **Interactive Elements**: Real-time feedback and animations

### Admin Interface
- **Dashboard**: Statistics cards with Chart.js visualizations
- **Data Tables**: Sortable, searchable tables with pagination
- **Modal Dialogs**: User-friendly forms for data entry
- **Responsive Navigation**: Dropdown menus and mobile-optimized layout

### Student Interface
- **Room Gallery**: Card-based layout with filtering options
- **Booking Flow**: Step-by-step booking process with validation
- **Personal Dashboard**: Clean overview of booking status
- **Interactive Filters**: Real-time room filtering by type and price

## 🔒 Security Features

### Authentication & Authorization
- **Password Security**: Werkzeug password hashing
- **Session Security**: Secure session management
- **Role Validation**: Decorator-based access control
- **Input Sanitization**: Protection against XSS attacks

### Database Security
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy
- **Data Validation**: Server-side input validation
- **Transaction Management**: ACID compliance with rollback support

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Features
- **Touch-Friendly**: Optimized for mobile interaction
- **Flexible Layouts**: CSS Grid and Flexbox
- **Optimized Images**: Responsive image loading
- **Progressive Enhancement**: Core functionality without JavaScript

## 🧪 Testing

### Manual Testing Checklist

#### Authentication
- [x] Admin login with correct credentials
- [x] Student registration and login
- [x] Invalid login attempts handling
- [x] Session management and timeout
- [x] Logout functionality

#### Admin Features
- [x] Dashboard statistics display
- [x] Student management operations
- [x] Room CRUD operations
- [x] Booking approval/rejection
- [x] Payment tracking

#### Student Features
- [x] Room browsing and filtering
- [x] Booking request submission
- [x] Personal dashboard view
- [x] Booking status tracking

#### Cross-Browser Compatibility
- [x] Chrome (latest)
- [x] Firefox (latest)
- [x] Safari (latest)
- [x] Edge (latest)

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Error
```
Error: Can't connect to MySQL server
```
**Solution**: Check MySQL service status and verify credentials

#### Module Import Error
```
ModuleNotFoundError: No module named 'flask_sqlalchemy'
```
**Solution**: Install dependencies with `pip install -r requirements.txt`

#### Table Doesn't Exist Error
```
Table 'hostel_managementv2.users' doesn't exist
```
**Solution**: Visit `/init-db` endpoint or restart the application

### Debug Mode
For development, enable debug mode:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 📊 Performance Optimization

### Frontend Optimizations
- **Minified Assets**: Compressed CSS and JavaScript
- **Efficient DOM Manipulation**: Optimized JavaScript functions
- **Debounced Search**: Improved search performance
- **Progressive Loading**: Lazy loading for large datasets

### Backend Optimizations
- **Database Indexing**: Optimized queries with proper indexes
- **Connection Pooling**: SQLAlchemy connection management
- **Query Optimization**: Efficient JOIN operations
- **Caching Strategy**: Session-based caching

## 🔮 Future Enhancements

### Planned Features
- **Email Notifications**: Automated booking confirmations
- **SMS Integration**: Real-time status updates
- **Payment Gateway**: Online payment processing
- **Advanced Analytics**: Detailed reporting dashboard
- **Mobile Application**: Native mobile app
- **Multi-language Support**: Internationalization

### Technical Improvements
- **API Documentation**: Swagger/OpenAPI integration
- **Unit Testing**: Comprehensive test suite
- **CI/CD Pipeline**: Automated deployment
- **Docker Support**: Containerized deployment
- **Redis Caching**: Performance optimization

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### Code Style Guidelines
- Follow PEP 8 for Python code
- Use consistent indentation (4 spaces)
- Comment complex logic
- Use meaningful variable names

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation for common solutions

## 📝 Changelog

### Version 1.0.0 (Current)
- ✅ Complete admin and student portals
- ✅ Room and booking management
- ✅ Payment tracking system
- ✅ Responsive design implementation
- ✅ Chart analytics dashboard
- ✅ Malaysian Ringgit (RM) currency support
- ✅ SQLAlchemy ORM integration
- ✅ Security enhancements

---

**Built with ❤️ for modern hostel management**
