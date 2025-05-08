# Health Check System

<p align="center">
  <img src="static/images/sky-logo.png" alt="Health Check System Logo" width="200">
</p>

A modern Django-based application for conducting team health checks and monitoring organization pulse. This system provides a beautiful, gradient-themed interface allowing different organizational roles to track, manage, and visualize team health metrics.

## ✨ Features

### User Management
- **Enhanced Authentication System** with secure account creation and login
- **Role-based Access Control** (Engineer, Team Leader, Department Leader, Senior Manager)
- **Password Recovery** system using favorite place verification
- **Profile Management** with team association and role selection

### Beautiful Interface
- **Modern Gradient Design** across all pages with consistent styling
- **Responsive Dashboard** layouts optimized for all devices
- **Interactive UI Elements** with hover effects and smooth animations
- **Custom Navigation** tailored to user roles

### Health Check System
- **Traffic Light Voting** system (green, amber, red) for intuitive health indicators
- **Session-based Health Checks** for periodic team assessment
- **Detailed Team Summaries** with visual health indicators
- **Department Overviews** for higher-level management
- **Organization-wide Health Monitoring** for senior leadership

### Administrative Functions
- **Comprehensive Admin Panel** for system management
- **Data Organization** by departments, teams, sessions, and health cards
- **User Management** capabilities for administrators

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/health_check_system.git
cd health_check_system
```

2. **Set up a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

If requirements.txt is not available, install the core dependencies:

```bash
pip install django pillow
```

4. **Apply database migrations**

```bash
python manage.py migrate
```

5. **Create an admin user**

```bash
python manage.py createsuperuser
```

6. **Run the development server**

```bash
python manage.py runserver
```

7. **Access the application** at: http://127.0.0.1:8000/

## 📋 Initial Configuration

After installation, follow these steps:

1. Login to the admin panel at http://127.0.0.1:8000/admin/ using your superuser credentials
2. Configure the system by creating:
   - **Departments** (e.g., Engineering, Marketing, Sales)
   - **Teams** within departments (e.g., Frontend, Backend, QA)
   - **Health Cards** for assessment categories (e.g., Delivery Confidence, Team Morale)
   - **Sessions** for periodic health checks (e.g., Q1 2023, May Sprint)

## 🖥️ Usage Guide

### Engineer Role
- Participate in health checks for your team
- View team health summaries
- Monitor active sessions
- Update your profile information

### Team Leader Role
- Conduct your own health checks
- View comprehensive team summaries
- Access department-level overviews
- Track team health metrics over time

### Department Leader Role
- Review all teams within your department
- Access department-wide health summaries
- Compare team performance across sessions
- Identify patterns and trends

### Senior Manager Role
- Get an organization-wide health overview
- Review metrics across all departments
- Access detailed reports by department
- Make informed decisions based on health trends

## 🎨 Customization

The system comes with a modern blue gradient theme, but you can customize the appearance:

- Edit CSS styles in template files to modify colors and gradients
- Add custom logos by replacing files in the static/images directory
- Extend the health card system with custom categories relevant to your organization

## 📱 Responsive Design

The application is fully responsive and works seamlessly on:
- Desktop browsers
- Tablets
- Mobile devices

## 🔒 Security Features

- Secure authentication system
- Password recovery using personal verification
- Role-based access control
- CSRF protection
- Secure form handling

## 📈 Future Enhancements

- Advanced analytics dashboard
- Email notifications for new sessions
- Integration with project management tools
- Customizable report generation
- Team action items and follow-ups

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 