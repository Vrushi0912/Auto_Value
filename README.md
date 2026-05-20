# Auto Value

Auto Value is a professional Flask-based web application that provides car price predictions and aggregated car listings.

## Features
- User Authentication (Sign up with Email OTP, Login, Password Reset)
- Car Price Prediction (Powered by Scikit-Learn)
- Aggregated Car Listings (from Spinny, Cars24, etc.)
- Interactive UI for filtering and searching

## Tech Stack
- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login
- **Database**: SQLite (SQLAlchemy ORM)
- **Machine Learning**: Scikit-Learn, Pandas, Numpy

## Local Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Auto_Value-main/Auto_Value-main
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   - Copy `.env.example` to `.env`
   - Fill in your `SECRET_KEY`, `EMAIL_USER`, and `EMAIL_PASS` (Use a Gmail App Password).

5. **Run the Application**
   ```bash
   flask run
   ```
   Or use Gunicorn (macOS/Linux):
   ```bash
   gunicorn main:app
   ```

## Deployment (Render)
This project is configured for easy deployment on [Render](https://render.com).
We use a **Persistent Disk** for the SQLite database so user data is not lost on deployments.

1. Create an account on Render.
2. Connect your GitHub repository.
3. Click **New +** > **Blueprint** and select this repository.
4. Render will automatically read the `render.yaml` and provision the Web Service and Persistent Disk.
5. In the Render Dashboard for your Web Service, go to **Environment** and add the actual values for `SECRET_KEY`, `EMAIL_USER`, and `EMAIL_PASS`.

## License
MIT License
