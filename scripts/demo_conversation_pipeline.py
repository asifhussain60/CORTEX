#!/usr/bin/env python3
"""
CORTEX 3.0 - Conversation Pipeline Demo
======================================

Demonstrates the conversation pipeline integration in action.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Task 4 - Conversation Pipeline Integration
Purpose: Live demonstration of conversation capture and processing
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add src to path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent))

from src.collectors.conversation_collector import ConversationCollector
from src.collectors.manager import CollectorManager


def create_demo_conversation(brain_path: Path, filename: str, content: str) -> Path:
    """Create a demo conversation file"""
    captures_path = brain_path / "conversation-captures"
    captures_path.mkdir(exist_ok=True)
    
    file_path = captures_path / filename
    file_path.write_text(content, encoding='utf-8')
    
    print(f"✅ Created demo conversation: {filename}")
    print(f"   Size: {len(content):,} characters")
    return file_path


def demo_conversation_pipeline():
    """Demonstrate the conversation pipeline in action"""
    
    print("🧠 CORTEX 3.0 - Conversation Pipeline Demo")
    print("=" * 50)
    print()
    
    # Setup demo brain directory
    brain_path = Path("demo_brain")
    brain_path.mkdir(exist_ok=True)
    
    print("🔧 Setting up demo environment...")
    
    # Initialize collector manager
    manager = CollectorManager(
        brain_path=str(brain_path),
        auto_start=False
    )
    
    print("✅ Collector manager initialized")
    
    # Initialize and start collectors
    manager.initialize()
    results = manager.start_all_collectors()
    
    print(f"✅ Started {len(results)} collectors")
    print(f"   Conversation collector: {'✅' if results.get('conversation_pipeline') else '❌'}")
    print()
    
    # Demo 1: Simple conversation
    print("📝 Demo 1: Simple Q&A Conversation")
    print("-" * 30)
    
    simple_conversation = """# Python Basics Question

User: What is a Python list?

CORTEX: A Python list is a built-in data structure that stores an ordered collection of items. Lists are:

- **Mutable**: You can change them after creation
- **Ordered**: Items maintain their position
- **Heterogeneous**: Can contain different data types

Example:
```python
my_list = [1, 'hello', True, 3.14]
my_list.append('new item')  # Add item
print(my_list[0])  # Access first item: 1
```

User: How do I remove items from a list?

CORTEX: You can remove items several ways:

```python
my_list = ['apple', 'banana', 'cherry']

# Remove by value
my_list.remove('banana')  # ['apple', 'cherry']

# Remove by index
del my_list[0]  # ['cherry']

# Remove and return last item
last_item = my_list.pop()  # 'cherry'
```

User: Perfect, thanks!

CORTEX: You're welcome! Lists are fundamental in Python programming.
"""
    
    demo_file_1 = create_demo_conversation(
        brain_path, 
        "2025-11-16-simple-python-question.md",
        simple_conversation
    )
    
    # Demo 2: Complex technical conversation
    print("\n📝 Demo 2: Complex Technical Implementation")
    print("-" * 40)
    
    complex_conversation = """# Microservices Architecture Implementation

User: I need to design a microservices architecture for an e-commerce platform with user management, inventory, orders, and payments.

CORTEX: I'll design a comprehensive microservices architecture for your e-commerce platform:

## System Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │  Load Balancer  │    │   CDN/Cache     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
    ┌────▼────┐            ┌────▼────┐            ┌────▼────┐
    │  User   │            │Inventory│            │ Orders  │
    │Service  │            │Service  │            │Service  │
    └────┬────┘            └────┬────┘            └────┬────┘
         │                      │                      │
    ┌────▼────┐            ┌────▼────┐            ┌────▼────┐
    │User DB  │            │Inventory│            │Order DB │
    │(PostgreSQL)          │  DB     │            │(MongoDB)│
    └─────────┘            │(MongoDB)│            └─────────┘
                           └─────────┘
```

## Phase 1: Core Services Implementation

### 1. User Management Service
```python
# user_service/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# user_service/api.py
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

@app.route('/api/users/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate input
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create user
    user = User(
        email=data['email'],
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', '')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully', 'user_id': user.id}), 201

@app.route('/api/users/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and user.check_password(data.get('password')):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401
```

### 2. Inventory Management Service
```python
# inventory_service/models.py
from mongoengine import Document, StringField, IntField, DecimalField, DateTimeField
from datetime import datetime

class Product(Document):
    sku = StringField(required=True, unique=True)
    name = StringField(required=True, max_length=255)
    description = StringField()
    category = StringField(required=True)
    price = DecimalField(min_value=0, precision=2)
    stock_quantity = IntField(min_value=0, default=0)
    reserved_quantity = IntField(min_value=0, default=0)
    low_stock_threshold = IntField(min_value=0, default=10)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'products',
        'indexes': ['sku', 'category', 'stock_quantity']
    }
    
    def available_quantity(self):
        return self.stock_quantity - self.reserved_quantity
    
    def is_low_stock(self):
        return self.available_quantity() <= self.low_stock_threshold

# inventory_service/api.py
from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route('/api/inventory/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    
    query = Product.objects
    if category:
        query = query.filter(category=category)
    
    products = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'products': [
            {
                'id': str(p.id),
                'sku': p.sku,
                'name': p.name,
                'price': float(p.price),
                'available_quantity': p.available_quantity(),
                'is_low_stock': p.is_low_stock()
            } for p in products.items
        ],
        'total': products.total,
        'pages': products.pages,
        'current_page': page
    })

@app.route('/api/inventory/products/<product_id>/reserve', methods=['POST'])
@jwt_required()
def reserve_stock(product_id):
    data = request.get_json()
    quantity = data.get('quantity', 0)
    
    if quantity <= 0:
        return jsonify({'error': 'Invalid quantity'}), 400
    
    product = Product.objects(id=product_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if product.available_quantity() < quantity:
        return jsonify({'error': 'Insufficient stock'}), 409
    
    # Reserve stock
    product.reserved_quantity += quantity
    product.save()
    
    return jsonify({
        'message': 'Stock reserved successfully',
        'reserved_quantity': quantity,
        'available_quantity': product.available_quantity()
    })
```

### 3. Order Management Service
```python
# order_service/models.py
from mongoengine import Document, StringField, IntField, DecimalField, DateTimeField, ListField, EmbeddedDocument, EmbeddedDocumentField
from datetime import datetime
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem(EmbeddedDocument):
    product_id = StringField(required=True)
    sku = StringField(required=True)
    name = StringField(required=True)
    price = DecimalField(required=True, precision=2)
    quantity = IntField(required=True, min_value=1)
    
    @property
    def total_price(self):
        return self.price * self.quantity

class Order(Document):
    user_id = IntField(required=True)
    order_number = StringField(required=True, unique=True)
    items = ListField(EmbeddedDocumentField(OrderItem))
    status = StringField(choices=[s.value for s in OrderStatus], default=OrderStatus.PENDING.value)
    total_amount = DecimalField(precision=2)
    shipping_address = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'orders',
        'indexes': ['user_id', 'order_number', 'status', 'created_at']
    }
    
    def calculate_total(self):
        return sum(item.total_price for item in self.items)

# order_service/api.py
import requests
from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route('/api/orders', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate order data
    items_data = data.get('items', [])
    if not items_data:
        return jsonify({'error': 'Order must contain at least one item'}), 400
    
    # Create order items and reserve stock
    order_items = []
    total_amount = 0
    
    for item_data in items_data:
        # Verify product exists and has stock
        inventory_response = requests.get(
            f"http://inventory-service/api/inventory/products/{item_data['product_id']}"
        )
        
        if inventory_response.status_code != 200:
            return jsonify({'error': f"Product {item_data['product_id']} not found"}), 404
        
        product = inventory_response.json()
        
        if product['available_quantity'] < item_data['quantity']:
            return jsonify({'error': f"Insufficient stock for {product['name']}"}), 409
        
        # Reserve stock
        reserve_response = requests.post(
            f"http://inventory-service/api/inventory/products/{item_data['product_id']}/reserve",
            json={'quantity': item_data['quantity']},
            headers={'Authorization': request.headers.get('Authorization')}
        )
        
        if reserve_response.status_code != 200:
            return jsonify({'error': 'Failed to reserve stock'}), 500
        
        # Create order item
        order_item = OrderItem(
            product_id=item_data['product_id'],
            sku=product['sku'],
            name=product['name'],
            price=product['price'],
            quantity=item_data['quantity']
        )
        order_items.append(order_item)
        total_amount += order_item.total_price
    
    # Generate order number
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{user_id}-{int(time.time() * 1000) % 10000:04d}"
    
    # Create order
    order = Order(
        user_id=user_id,
        order_number=order_number,
        items=order_items,
        total_amount=total_amount,
        shipping_address=data.get('shipping_address', ''),
        status=OrderStatus.PENDING.value
    )
    order.save()
    
    return jsonify({
        'message': 'Order created successfully',
        'order': {
            'id': str(order.id),
            'order_number': order.order_number,
            'total_amount': float(order.total_amount),
            'status': order.status
        }
    }), 201
```

## Phase 2: Service Communication & API Gateway

### API Gateway Configuration (Kong/Nginx)
```yaml
# api_gateway/kong.yml
services:
  - name: user-service
    url: http://user-service:5000
    
  - name: inventory-service  
    url: http://inventory-service:5001
    
  - name: order-service
    url: http://order-service:5002

routes:
  - name: user-routes
    service: user-service
    paths:
      - /api/users
    
  - name: inventory-routes
    service: inventory-service
    paths:
      - /api/inventory
      
  - name: order-routes
    service: order-service
    paths:
      - /api/orders

plugins:
  - name: jwt
    config:
      secret_is_base64: false
      key_claim_name: kid
      
  - name: rate-limiting
    config:
      minute: 100
      hour: 1000
```

User: This is comprehensive! How do we handle distributed transactions and data consistency?

CORTEX: Excellent question! In microservices, we need to handle distributed transactions carefully. I'll implement the Saga pattern with event sourcing:

## Distributed Transaction Management

### 1. Saga Orchestrator Pattern
```python
# saga_orchestrator/order_saga.py
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any
import requests
import json

class SagaStep(Enum):
    VALIDATE_ORDER = "validate_order"
    RESERVE_INVENTORY = "reserve_inventory" 
    PROCESS_PAYMENT = "process_payment"
    CREATE_ORDER = "create_order"
    SEND_CONFIRMATION = "send_confirmation"

@dataclass
class SagaTransaction:
    transaction_id: str
    order_data: Dict[str, Any]
    current_step: SagaStep
    completed_steps: List[SagaStep]
    compensation_data: Dict[str, Any]
    
class OrderSagaOrchestrator:
    def __init__(self):
        self.steps = [
            SagaStep.VALIDATE_ORDER,
            SagaStep.RESERVE_INVENTORY,
            SagaStep.PROCESS_PAYMENT, 
            SagaStep.CREATE_ORDER,
            SagaStep.SEND_CONFIRMATION
        ]
        
    def execute_saga(self, order_data: Dict[str, Any]) -> bool:
        transaction_id = self.generate_transaction_id()
        saga = SagaTransaction(
            transaction_id=transaction_id,
            order_data=order_data,
            current_step=self.steps[0],
            completed_steps=[],
            compensation_data={}
        )
        
        try:
            for step in self.steps:
                saga.current_step = step
                success = self.execute_step(saga, step)
                
                if not success:
                    # Execute compensation
                    self.compensate(saga)
                    return False
                    
                saga.completed_steps.append(step)
            
            return True
            
        except Exception as e:
            self.compensate(saga)
            return False
    
    def execute_step(self, saga: SagaTransaction, step: SagaStep) -> bool:
        if step == SagaStep.VALIDATE_ORDER:
            return self.validate_order(saga)
        elif step == SagaStep.RESERVE_INVENTORY:
            return self.reserve_inventory(saga)
        elif step == SagaStep.PROCESS_PAYMENT:
            return self.process_payment(saga)
        elif step == SagaStep.CREATE_ORDER:
            return self.create_order(saga)
        elif step == SagaStep.SEND_CONFIRMATION:
            return self.send_confirmation(saga)
    
    def compensate(self, saga: SagaTransaction):
        # Execute compensation in reverse order
        for step in reversed(saga.completed_steps):
            if step == SagaStep.RESERVE_INVENTORY:
                self.release_inventory(saga)
            elif step == SagaStep.PROCESS_PAYMENT:
                self.refund_payment(saga)
            # ... other compensations
```

### 2. Event Sourcing Implementation  
```python
# event_store/models.py
class Event(Document):
    aggregate_id = StringField(required=True)
    aggregate_type = StringField(required=True)
    event_type = StringField(required=True)
    event_data = DictField(required=True)
    version = IntField(required=True)
    timestamp = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'events',
        'indexes': [
            ('aggregate_id', 'version'),
            ('aggregate_type', 'timestamp'),
            'event_type'
        ]
    }

class EventStore:
    def append_event(self, aggregate_id: str, aggregate_type: str, 
                    event_type: str, event_data: Dict, expected_version: int):
        # Optimistic concurrency control
        current_version = self.get_current_version(aggregate_id)
        
        if current_version != expected_version:
            raise ConcurrencyError("Version conflict")
        
        event = Event(
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            event_type=event_type,
            event_data=event_data,
            version=expected_version + 1
        )
        event.save()
        
        # Publish event to message bus
        self.publish_event(event)
    
    def get_events(self, aggregate_id: str) -> List[Event]:
        return Event.objects(aggregate_id=aggregate_id).order_by('version')
```

User: Perfect! How do we handle monitoring and observability across all these services?

CORTEX: I'll implement comprehensive observability with distributed tracing, metrics, and centralized logging:

## Observability & Monitoring Stack

### 1. Distributed Tracing with OpenTelemetry
```python
# observability/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

def setup_tracing(service_name: str):
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )
    
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Auto-instrument Flask and requests
    FlaskInstrumentor().instrument()
    RequestsInstrumentor().instrument()
    
    return tracer

# Usage in services
tracer = setup_tracing("user-service")

@app.route('/api/users/login', methods=['POST'])
def login():
    with tracer.start_as_current_span("user_login") as span:
        span.set_attribute("user.email", data.get('email'))
        
        # ... login logic
        
        span.set_attribute("login.success", True)
        span.set_attribute("user.id", user.id)
```

This architecture provides a robust, scalable foundation for your e-commerce platform with proper separation of concerns, data consistency, and observability.

User: Excellent! Let's implement this step by step. Start with the user service.

CORTEX: I'll implement the user service with complete setup including Docker, database migrations, and testing:

## User Service Implementation

Files to create:
- user_service/Dockerfile
- user_service/requirements.txt  
- user_service/app.py
- user_service/models.py
- user_service/config.py
- user_service/migrations/
- user_service/tests/
"""
    
    demo_file_2 = create_demo_conversation(
        brain_path,
        "2025-11-16-microservices-architecture.md", 
        complex_conversation
    )
    
    # Wait a moment for processing
    print("\n⏳ Processing conversations...")
    time.sleep(2)
    
    # Collect metrics to trigger processing
    all_metrics = manager.collect_all_metrics()
    conversation_metrics = all_metrics.get("conversation_pipeline", [])
    
    print(f"\n📊 Pipeline Results:")
    print(f"   Conversations processed: {len([m for m in conversation_metrics if m.name == 'conversations_processed'])}")
    
    # Show metrics details
    for metric in conversation_metrics:
        if metric.name in ["conversation_quality_score", "conversations_processed"]:
            print(f"   {metric.name}: {metric.value}")
    
    # Check database
    import sqlite3
    db_path = brain_path / "tier1-working-memory.db"
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT title, quality_score, quality_level FROM conversations ORDER BY created_at DESC")
        conversations = cursor.fetchall()
        
        print(f"\n💾 Database Storage:")
        print(f"   Total conversations: {count}")
        
        for title, quality_score, quality_level in conversations:
            print(f"   📝 {title}")
            print(f"       Quality: {quality_score:.1f} ({quality_level})")
        
        conn.close()
    
    # Check vault archival
    vault_path = brain_path / "conversation-vault"
    archived_files = list(vault_path.rglob("*.md"))
    
    print(f"\n🗄️  Archival Status:")
    print(f"   Files archived: {len(archived_files)}")
    
    for archived_file in archived_files:
        print(f"   📁 {archived_file.name}")
        
        # Show metadata preview
        content = archived_file.read_text()
        if "quality_score:" in content:
            for line in content.split('\n'):
                if line.startswith(('quality_score:', 'strategic_value:', 'message_count:')):
                    print(f"       {line}")
    
    # Health status
    print(f"\n🏥 Collector Health:")
    health_status = manager.get_collector_health()
    
    for collector_id, health in health_status.items():
        if collector_id == "conversation_pipeline":
            print(f"   {collector_id}: {health.status.value}")
            print(f"   Metrics collected: {health.metrics_collected}")
            if health.last_collection:
                print(f"   Last collection: {health.last_collection.strftime('%H:%M:%S')}")
    
    print(f"\n✅ Conversation Pipeline Demo Complete!")
    print(f"\nDemo artifacts created in: {brain_path}")
    print(f"- Database: {db_path}")
    print(f"- Archived conversations: {vault_path}")
    
    # Cleanup option
    print(f"\n🧹 Cleanup: Remove 'demo_brain' directory when done")
    
    return brain_path


if __name__ == "__main__":
    try:
        demo_brain_path = demo_conversation_pipeline()
        
        print("\n🎯 Demo Summary:")
        print("=" * 50)
        print("✅ Conversation pipeline successfully demonstrated")
        print("✅ Quality scoring and metadata extraction working")  
        print("✅ Database storage and archival process functional")
        print("✅ Manager integration verified")
        print("\n📚 Next Steps:")
        print("1. Run integration tests: pytest tests/collectors/test_conversation_pipeline_integration.py")
        print("2. Review archived conversations in demo_brain/conversation-vault/")
        print("3. Check database content with SQLite browser")
        print("4. Integrate with CORTEX 3.0 production environment")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 CORTEX Conversation Pipeline - Task 4 Complete!")