from flask import Flask,render_template,request,jsonify,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Numeric
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime,date
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/hostel_managementV2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100),unique=True,nullable=False)
    phone = db.Column(db.String(15))
    password = db.Column(db.String(255),nullable=False)
    role = db.Column(db.Enum('admin','student'),nullable=False,default='student')
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

    # relationships
    bookings = db.relationship('Booking',backref='user',lazy=True,cascade='all, delete-orphan')

    def set_password(self,password):
        self.password = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password,password)

    def __repr__(self):
        return f'<User {self.email}>'


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer,primary_key=True)
    room_number = db.Column(db.String(10),unique=True,nullable=False)
    room_type = db.Column(db.Enum('single','double','triple','quad'),nullable=False)
    capacity = db.Column(db.Integer,nullable=False)
    rent_per_month = db.Column(Numeric(10,2),nullable=False)
    amenities = db.Column(db.Text)
    is_available = db.Column(db.Boolean,default=True)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

    # relationships
    bookings = db.relationship('Booking',backref='room',lazy=True,cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Room {self.room_number}>'


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    room_id = db.Column(db.Integer,db.ForeignKey('rooms.id'),nullable=False)
    start_date = db.Column(db.Date,nullable=False)
    end_date = db.Column(db.Date)
    status = db.Column(db.Enum('pending','approved','rejected','active','completed'),
                       default='pending')
    total_amount = db.Column(Numeric(10,2))
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

    # relationships
    payments = db.relationship('Payment',backref='booking',lazy=True,cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Booking {self.id}>'


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer,primary_key=True)
    booking_id = db.Column(db.Integer,db.ForeignKey('bookings.id'),nullable=False)
    amount = db.Column(Numeric(10,2),nullable=False)
    payment_date = db.Column(db.Date,nullable=False)
    payment_method = db.Column(db.Enum('cash','online','card'),default='cash')
    status = db.Column(db.Enum('pending','completed','failed'),default='pending')
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

    def __repr__(self):
        return f'<Payment {self.id}>'


# initialize the database
def init_db():
    with app.app_context():
        try:
            # test the database connection first
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT 1"))
            print("✅ Database connection successful!")

            # then create all the tables
            db.create_all()
            print("✅ Database tables created successfully!")

            # create admin user if not exists -- for initial setup only, should happen once
            admin_user = User.query.filter_by(email='admin@hostel.com').first()
            if not admin_user:
                admin = User(
                    name='Admin User',
                    email='admin@hostel.com',
                    role='admin'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                print("✅ Admin user created!")
            else:
                print("ℹ️  Admin user already exists")

            # create sample rooms if not exists
            if Room.query.count() == 0:
                sample_rooms = [
                    Room(room_number='A101',room_type='single',capacity=1,
                         rent_per_month=1200.00,amenities='AC, WiFi, Study Table, Wardrobe'),
                    Room(room_number='A102',room_type='single',capacity=1,
                         rent_per_month=1200.00,amenities='AC, WiFi, Study Table, Wardrobe'),
                    Room(room_number='B201',room_type='double',capacity=2,
                         rent_per_month=1800.00,amenities='AC, WiFi, Study Tables, Wardrobes, Balcony'),
                    Room(room_number='B202',room_type='double',capacity=2,
                         rent_per_month=1800.00,amenities='AC, WiFi, Study Tables, Wardrobes'),
                    Room(room_number='C301',room_type='triple',capacity=3,
                         rent_per_month=2400.00,amenities='AC, WiFi, Study Tables, Wardrobes, Common Area'),
                    Room(room_number='D401',room_type='quad',capacity=4,
                         rent_per_month=3000.00,amenities='AC, WiFi, Study Tables, Wardrobes, Kitchen Access'),
                ]

                for room in sample_rooms:
                    db.session.add(room)
                print("✅ Sample rooms created!")
            else:
                print("ℹ️  Sample rooms already exist")

            db.session.commit()
            print("✅ Database initialization completed successfully!")

            # verify if tables were created or not
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tables in database: {tables}")

        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            db.session.rollback()
            raise e


# Authentication functions
def login_required(f):
    def decorated_function(*args,**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args,**kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


def admin_required(f):
    def decorated_function(*args,**kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required','error')
            return redirect(url_for('dashboard'))
        return f(*args,**kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


# Routes -- main application logic
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/init-db')
def init_database():
    """Manual database initialization route"""
    try:
        init_db()
        return jsonify({'success': True,'message': 'Database initialized successfully!'})
    except Exception as e:
        return jsonify({'success': False,'message': f'Error: {str(e)}'})


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['name'] = user.name
            session['email'] = user.email
            session['role'] = user.role
            flash('Login successful!','success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!','error')

    return render_template('login.html')


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # check if user already exists - this ensures no duplicate registrations
        if User.query.filter_by(email=email).first():
            flash('Email already exists!','error')
            return render_template('register.html')

        # create a new user
        user = User(name=name,email=email,phone=phone,role='student')
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.','success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!','info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    if session['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # get stats
    total_students = User.query.filter_by(role='student').count()
    total_rooms = Room.query.count()
    available_rooms = Room.query.filter_by(is_available=True).count()
    active_bookings = Booking.query.filter_by(status='active').count()

    # get the total revenue
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(status='completed').scalar()
    total_revenue = float(total_revenue) if total_revenue else 0

    pending_requests = Booking.query.filter_by(status='pending').count()

    stats = {
        'total_students': total_students,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'active_bookings': active_bookings,
        'total_revenue': total_revenue,
        'pending_requests': pending_requests
    }

    return render_template('admin_dashboard.html',stats=stats)


@app.route('/student/dashboard')
@login_required
def student_dashboard():
    # Get a user current booking
    current_booking = db.session.query(Booking,Room).join(Room).filter(
        Booking.user_id == session['user_id'],
        Booking.status.in_(['pending','approved','active'])
    ).order_by(Booking.created_at.desc()).first()

    # Get all available rooms
    available_rooms = Room.query.filter_by(is_available=True).order_by(Room.room_number).all()

    # convert current_booking to dict type if it exists
    booking_data = None
    if current_booking:
        booking,room = current_booking
        booking_data = {
            'id': booking.id,
            'start_date': booking.start_date,
            'status': booking.status,
            'total_amount': booking.total_amount,
            'room_number': room.room_number,
            'room_type': room.room_type,
            'rent_per_month': room.rent_per_month
        }

    return render_template('student_dashboard.html',
                           current_booking=booking_data,
                           available_rooms=available_rooms)


# admin Routes -- DON'T MESS WITH THESE UNLESS YOU KNOW WHAT YOU ARE DOING,
# if you do, make sure to thoroughly test and test pages privileges and make
# sure no one other than admin can access these pages BUT
# IF YOU DO DON'T!!!
@app.route('/admin/students')
@admin_required
def admin_students():
    students = User.query.filter_by(role='student').order_by(User.created_at.desc()).all()
    return render_template('admin_students.html',students=students)


@app.route('/admin/rooms')
@admin_required
def admin_rooms():
    rooms = Room.query.order_by(Room.room_number).all()
    return render_template('admin_rooms.html',rooms=rooms)


@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    bookings = db.session.query(Booking,User,Room).join(User).join(Room).order_by(Booking.created_at.desc()).all()

    # Convert to list of dicts for template
    booking_list = []
    for booking,user,room in bookings:
        booking_list.append({
            'id': booking.id,
            'start_date': booking.start_date,
            'status': booking.status,
            'total_amount': booking.total_amount,
            'created_at': booking.created_at,
            'student_name': user.name,
            'email': user.email,
            'room_number': room.room_number,
            'room_type': room.room_type
        })

    return render_template('admin_bookings.html',bookings=booking_list)


@app.route('/admin/payments')
@admin_required
def admin_payments():
    # Fixed query with explicit select_from
    payments = db.session.query(Payment,Booking,User,Room) \
        .select_from(Payment) \
        .join(Booking,Payment.booking_id == Booking.id) \
        .join(User,Booking.user_id == User.id) \
        .join(Room,Booking.room_id == Room.id) \
        .order_by(Payment.created_at.desc()).all()

    # Convert to list of dicts for template
    payment_list = []
    for payment,booking,user,room in payments:
        payment_list.append({
            'id': payment.id,
            'amount': payment.amount,
            'payment_date': payment.payment_date,
            'payment_method': payment.payment_method,
            'status': payment.status,
            'created_at': payment.created_at,
            'booking_id': booking.id,
            'student_name': user.name,
            'room_number': room.room_number
        })

    return render_template('admin_payments.html',payments=payment_list)


# API Routes
@app.route('/api/rooms/add',methods=['POST'])
@admin_required
def add_room():
    try:
        data = request.get_json()

        # Check if the room number already does exist
        if Room.query.filter_by(room_number=data['room_number']).first():
            return jsonify({'success': False,'message': 'Room number already exists'})

        room = Room(
            room_number=data['room_number'],
            room_type=data['room_type'],
            capacity=data['capacity'],
            rent_per_month=data['rent_per_month'],
            amenities=data['amenities']
        )

        db.session.add(room)
        db.session.commit()

        return jsonify({'success': True,'message': 'Room added successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False,'message': str(e)})


@app.route('/api/rooms/<int:room_id>/update',methods=['PUT'])
@admin_required
def update_room(room_id):
    try:
        data = request.get_json()
        room = Room.query.get_or_404(room_id)

        room.room_number = data['room_number']
        room.room_type = data['room_type']
        room.capacity = data['capacity']
        room.rent_per_month = data['rent_per_month']
        room.amenities = data['amenities']
        room.is_available = data['is_available']

        db.session.commit()

        return jsonify({'success': True,'message': 'Room updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False,'message': str(e)})


@app.route('/api/rooms/<int:room_id>/delete',methods=['DELETE'])
@admin_required
def delete_room(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        db.session.delete(room)
        db.session.commit()

        return jsonify({'success': True,'message': 'Room deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False,'message': str(e)})


@app.route('/api/bookings/request',methods=['POST'])
@login_required
def request_booking():
    try:
        data = request.get_json()

        # check if a user already has an active booking - this prevents multiple bookings
        existing_booking = Booking.query.filter_by(
            user_id=session['user_id']
        ).filter(Booking.status.in_(['pending','approved','active'])).first()

        if existing_booking:
            return jsonify({'success': False,'message': 'You already have an active booking'})

        # get the room details
        room = Room.query.get(data['room_id'])
        if not room:
            return jsonify({'success': False,'message': 'Room not found'})

        # create the booking
        booking = Booking(
            user_id=session['user_id'],
            room_id=data['room_id'],
            start_date=datetime.strptime(data['start_date'],'%Y-%m-%d').date(),
            total_amount=room.rent_per_month,
            status='pending'
        )

        db.session.add(booking)
        db.session.commit()

        return jsonify({'success': True,'message': 'Booking request submitted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False,'message': str(e)})


@app.route('/api/bookings/<int:booking_id>/approve',methods=['POST'])
@admin_required
def approve_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        room = Room.query.get(booking.room_id)

        booking.status = 'approved'
        room.is_available = False

        db.session.commit()

        return jsonify({'success': True,'message': 'Booking approved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False,'message': str(e)})


@app.route('/api/bookings/<int:booking_id>/reject',methods=['POST'])
@admin_required
def reject_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        booking.status = 'rejected'

        db.session.commit()

        return jsonify({'success': True,'message': 'Booking rejected'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False,'message': str(e)})


@app.route('/api/dashboard/stats')
@admin_required
def dashboard_stats():
    try:
        # Monthly revenue data (mock data for now)
        revenue_data = [
            {'month': '2024-01','revenue': 50000},
            {'month': '2024-02','revenue': 75000},
            {'month': '2024-03','revenue': 60000},
            {'month': '2024-04','revenue': 80000},
            {'month': '2024-05','revenue': 95000},
            {'month': '2024-06','revenue': 85000},
        ]

        # room occupancy data
        occupancy_data = db.session.query(
            Room.room_type,
            db.func.count(Room.id).label('total'),
            db.func.sum(db.case([(Room.is_available == False,1)],else_=0)).label('occupied')
        ).group_by(Room.room_type).all()

        occupancy_list = []
        for row in occupancy_data:
            occupancy_list.append({
                'room_type': row.room_type,
                'total': row.total,
                'occupied': row.occupied
            })

        return jsonify({
            'revenue_data': revenue_data,
            'occupancy_data': occupancy_list
        })
    except Exception as e:
        return jsonify({'success': False,'message': str(e)})


if __name__ == '__main__':
    # force database initialization on startup
    print("Starting Flask application...")
    print("Initializing database...")
    init_db()
    print("Database initialization complete!")
    app.run(debug=True)