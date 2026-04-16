# 🏠 Cebu Room Rental System

A complete web application for renting rooms, boarding houses, apartments, condominiums, dorms, and Airbnbs in Cebu City and Lapu-Lapu City.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [License](#license)

## ✨ Features

### User Roles

- **Tenant (Lister)** - Can post and manage rental listings
- **Buyer (Renter)** - Can browse, search, and book rooms

### Core Functionality

- ✅ User registration and authentication
- ✅ Create, edit, and delete rental listings
- ✅ Upload up to 3 images per listing (stored permanently on Cloudinary)
- ✅ Search and filter by:
  - Location (Cebu City / Lapu-Lapu City)
  - Property type (Boarding House, Apartment, Condo, Dorm, Airbnb)
  - Price range
  - Number of occupants
- ✅ Interactive map showing all listings (Leaflet.js)
- ✅ Booking system with status management (Pending, Confirmed, Cancelled, Completed)
- ✅ Messaging system between tenants and buyers
- ✅ User profiles with profile pictures
- ✅ Responsive design for mobile and desktop

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Django 6.0 | Backend web framework |
| PostgreSQL (Supabase) | Production database |
| Cloudinary | Cloud image storage |
| HTML5, CSS3 | Frontend structure and styling |
| Bootstrap 5 | Responsive UI framework |
| Leaflet.js | Interactive maps (free, no API key) |
| Vercel | Hosting and deployment |

## 📥 Installation

### Prerequisites

- Python 3.8 or higher
- Git (optional, for cloning)
- Supabase account (for database)
- Cloudinary account (for image storage)

### Step 1: Clone or Download the Project

```bash
# Clone the repository
git clone https://github.com/cherlsjastyn/cebu-room-rental.git

# Or download manually and extract the ZIP file