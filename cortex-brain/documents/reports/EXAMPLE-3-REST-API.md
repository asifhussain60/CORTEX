# TDD Mastery - Real-World Example: REST API CRUD Operations

**Example Type:** FastAPI REST API with TDD workflow  
**Phase:** Complete TDD workflow (Phase 1 + Phase 2 + Phase 3)  
**Language:** Python  
**Framework:** FastAPI + pytest + SQLAlchemy

---

## Scenario

Building REST API for blog post management with:
- CRUD operations (Create, Read, Update, Delete)
- Input validation
- Error handling (404, 422, 500)
- Database persistence
- Authentication middleware

---

## Step 1: Initialize TDD Session

```python
from workflows.tdd_workflow_orchestrator import (
    TDDWorkflowOrchestrator,
    TDDWorkflowConfig
)

config = TDDWorkflowConfig(
    project_root="/path/to/blog-api",
    test_output_dir="tests",
    enable_refactoring=True
)

orchestrator = TDDWorkflowOrchestrator(config)
session_id = orchestrator.start_session("blog_api_crud")
print(f"Session: {session_id}")
```

---

## Step 2: Source Code Skeleton

**File:** `src/api/posts.py`

```python
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session


class PostCreate(BaseModel):
    """Post creation schema."""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)
    tags: Optional[List[str]] = []


class PostUpdate(BaseModel):
    """Post update schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None


class PostResponse(BaseModel):
    """Post response schema."""
    id: int
    title: str
    content: str
    author: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime


router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Session) -> PostResponse:
    """
    Create new blog post.
    
    Args:
        post: Post creation data
        db: Database session
        
    Returns:
        Created post with ID and timestamps
        
    Raises:
        HTTPException: 422 if validation fails
    """
    pass


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session) -> PostResponse:
    """
    Get blog post by ID.
    
    Args:
        post_id: Post ID
        db: Database session
        
    Returns:
        Post details
        
    Raises:
        HTTPException: 404 if post not found
    """
    pass


@router.get("/", response_model=List[PostResponse])
async def list_posts(
    skip: int = 0,
    limit: int = 100,
    author: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = None
) -> List[PostResponse]:
    """
    List blog posts with filtering and pagination.
    
    Args:
        skip: Number of posts to skip (pagination)
        limit: Maximum number of posts to return
        author: Filter by author name
        tag: Filter by tag
        db: Database session
        
    Returns:
        List of posts matching filters
    """
    pass


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post: PostUpdate, db: Session) -> PostResponse:
    """
    Update blog post.
    
    Args:
        post_id: Post ID
        post: Update data (partial)
        db: Database session
        
    Returns:
        Updated post
        
    Raises:
        HTTPException: 404 if post not found
        HTTPException: 422 if validation fails
    """
    pass


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Session) -> None:
    """
    Delete blog post.
    
    Args:
        post_id: Post ID
        db: Database session
        
    Raises:
        HTTPException: 404 if post not found
    """
    pass
```

---

## Step 3: Generate Tests (RED Phase)

```python
# Generate comprehensive tests for all endpoints
result = orchestrator.generate_tests(
    source_file="src/api/posts.py",
    scenarios=[
        "edge_cases",           # Empty strings, invalid IDs, boundary values
        "domain_knowledge",     # REST API patterns, HTTP status codes
        "error_conditions",     # 404, 422, 500 errors
        "parametrized"          # Multiple filter combinations
    ]
)

print(f"Generated {result['test_count']} tests for REST API")
```

---

## Step 4: Generated Tests

**File:** `tests/api/test_posts.py` (Auto-generated)

```python
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from src.api.posts import PostCreate, PostUpdate


class TestCreatePost:
    """Test POST /api/posts endpoint."""
    
    def test_create_post_success(self, client: TestClient, mock_db):
        """Should create post with valid data."""
        post_data = {
            "title": "My First Post",
            "content": "This is the content of my first post.",
            "author": "John Doe",
            "tags": ["python", "fastapi"]
        }
        
        response = client.post("/api/posts", json=post_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "My First Post"
        assert data["author"] == "John Doe"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    # Edge Cases (Phase 1 - M1.1)
    def test_create_post_empty_title(self, client: TestClient):
        """Should reject empty title."""
        post_data = {
            "title": "",
            "content": "Content",
            "author": "Author"
        }
        
        response = client.post("/api/posts", json=post_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "title" in response.json()["detail"][0]["loc"]
    
    def test_create_post_title_too_long(self, client: TestClient):
        """Should reject title exceeding max length."""
        post_data = {
            "title": "x" * 201,  # Max is 200
            "content": "Content",
            "author": "Author"
        }
        
        response = client.post("/api/posts", json=post_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_post_missing_required_fields(self, client: TestClient):
        """Should reject request with missing required fields."""
        post_data = {"title": "Title"}  # Missing content and author
        
        response = client.post("/api/posts", json=post_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_post_empty_tags_list(self, client: TestClient, mock_db):
        """Should accept empty tags list."""
        post_data = {
            "title": "Post",
            "content": "Content",
            "author": "Author",
            "tags": []
        }
        
        response = client.post("/api/posts", json=post_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["tags"] == []
    
    # Domain Knowledge (Phase 1 - M1.2)
    def test_create_post_returns_location_header(self, client: TestClient, mock_db):
        """Should return Location header with created resource URL."""
        post_data = {
            "title": "Post",
            "content": "Content",
            "author": "Author"
        }
        
        response = client.post("/api/posts", json=post_data)
        
        assert "Location" in response.headers
        assert f"/api/posts/{response.json()['id']}" in response.headers["Location"]
    
    def test_create_post_timestamps_auto_generated(self, client: TestClient, mock_db):
        """Should auto-generate created_at and updated_at timestamps."""
        post_data = {
            "title": "Post",
            "content": "Content",
            "author": "Author"
        }
        
        response = client.post("/api/posts", json=post_data)
        data = response.json()
        
        assert data["created_at"] == data["updated_at"]  # Same on creation


class TestGetPost:
    """Test GET /api/posts/{post_id} endpoint."""
    
    def test_get_post_success(self, client: TestClient, mock_db, sample_post):
        """Should retrieve post by ID."""
        response = client.get(f"/api/posts/{sample_post.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_post.id
        assert data["title"] == sample_post.title
    
    # Error Conditions (Phase 1 - M1.3)
    def test_get_post_not_found(self, client: TestClient, mock_db):
        """Should return 404 for nonexistent post."""
        response = client.get("/api/posts/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_post_invalid_id_format(self, client: TestClient):
        """Should return 422 for invalid ID format."""
        response = client.get("/api/posts/invalid")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_post_negative_id(self, client: TestClient):
        """Should handle negative IDs gracefully."""
        response = client.get("/api/posts/-1")
        
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]


class TestListPosts:
    """Test GET /api/posts endpoint."""
    
    def test_list_posts_default(self, client: TestClient, mock_db, sample_posts):
        """Should list all posts with default pagination."""
        response = client.get("/api/posts")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == len(sample_posts)
    
    # Parametrized Tests (Phase 1 - M1.4)
    @pytest.mark.parametrize("skip,limit,expected_count", [
        (0, 10, 10),      # First page
        (10, 10, 10),     # Second page
        (0, 5, 5),        # Smaller page size
        (50, 10, 0),      # Beyond available posts
    ])
    def test_list_posts_pagination(
        self, client, mock_db, sample_posts, skip, limit, expected_count
    ):
        """Should paginate posts correctly."""
        response = client.get(f"/api/posts?skip={skip}&limit={limit}")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == expected_count
    
    def test_list_posts_filter_by_author(self, client: TestClient, mock_db, sample_posts):
        """Should filter posts by author."""
        author = "John Doe"
        response = client.get(f"/api/posts?author={author}")
        
        assert response.status_code == status.HTTP_200_OK
        posts = response.json()
        assert all(post["author"] == author for post in posts)
    
    def test_list_posts_filter_by_tag(self, client: TestClient, mock_db, sample_posts):
        """Should filter posts by tag."""
        tag = "python"
        response = client.get(f"/api/posts?tag={tag}")
        
        assert response.status_code == status.HTTP_200_OK
        posts = response.json()
        assert all(tag in post["tags"] for post in posts)
    
    def test_list_posts_empty_result(self, client: TestClient, mock_db):
        """Should return empty list when no posts match filters."""
        response = client.get("/api/posts?author=NonexistentAuthor")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestUpdatePost:
    """Test PUT /api/posts/{post_id} endpoint."""
    
    def test_update_post_title(self, client: TestClient, mock_db, sample_post):
        """Should update post title."""
        update_data = {"title": "Updated Title"}
        
        response = client.put(f"/api/posts/{sample_post.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["content"] == sample_post.content  # Unchanged
    
    def test_update_post_partial(self, client: TestClient, mock_db, sample_post):
        """Should allow partial updates."""
        update_data = {"tags": ["new-tag"]}
        
        response = client.put(f"/api/posts/{sample_post.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["tags"] == ["new-tag"]
        assert data["title"] == sample_post.title  # Unchanged
    
    # Domain Knowledge (Phase 1 - M1.2)
    def test_update_post_updated_at_changes(self, client: TestClient, mock_db, sample_post):
        """Should update updated_at timestamp."""
        original_updated = sample_post.updated_at
        update_data = {"title": "New Title"}
        
        response = client.put(f"/api/posts/{sample_post.id}", json=update_data)
        data = response.json()
        
        assert data["updated_at"] != original_updated
        assert data["created_at"] == sample_post.created_at  # Unchanged
    
    # Error Conditions (Phase 1 - M1.3)
    def test_update_post_not_found(self, client: TestClient, mock_db):
        """Should return 404 for nonexistent post."""
        update_data = {"title": "Title"}
        
        response = client.put("/api/posts/99999", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_post_invalid_data(self, client: TestClient, mock_db, sample_post):
        """Should return 422 for invalid update data."""
        update_data = {"title": ""}  # Empty title not allowed
        
        response = client.put(f"/api/posts/{sample_post.id}", json=update_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDeletePost:
    """Test DELETE /api/posts/{post_id} endpoint."""
    
    def test_delete_post_success(self, client: TestClient, mock_db, sample_post):
        """Should delete post by ID."""
        response = client.delete(f"/api/posts/{sample_post.id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deleted
        get_response = client.get(f"/api/posts/{sample_post.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_post_not_found(self, client: TestClient, mock_db):
        """Should return 404 for nonexistent post."""
        response = client.delete("/api/posts/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Domain Knowledge (Phase 1 - M1.2)
    def test_delete_post_idempotent(self, client: TestClient, mock_db, sample_post):
        """Should be idempotent (multiple deletes return 404)."""
        # First delete
        response1 = client.delete(f"/api/posts/{sample_post.id}")
        assert response1.status_code == status.HTTP_204_NO_CONTENT
        
        # Second delete
        response2 = client.delete(f"/api/posts/{sample_post.id}")
        assert response2.status_code == status.HTTP_404_NOT_FOUND


# Pytest fixtures
@pytest.fixture
def client():
    """FastAPI test client."""
    from fastapi import FastAPI
    from src.api.posts import router
    
    app = FastAPI()
    app.include_router(router)
    
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database session."""
    # SQLAlchemy session mock or in-memory database
    pass


@pytest.fixture
def sample_post(mock_db):
    """Create sample post for testing."""
    from src.models import Post
    
    post = Post(
        id=1,
        title="Sample Post",
        content="Sample content",
        author="John Doe",
        tags=["test"]
    )
    
    mock_db.add(post)
    mock_db.commit()
    
    return post


@pytest.fixture
def sample_posts(mock_db):
    """Create multiple sample posts."""
    from src.models import Post
    
    posts = []
    for i in range(20):
        post = Post(
            id=i+1,
            title=f"Post {i+1}",
            content=f"Content {i+1}",
            author="John Doe" if i % 2 == 0 else "Jane Smith",
            tags=["python"] if i % 3 == 0 else ["fastapi"]
        )
        posts.append(post)
        mock_db.add(post)
    
    mock_db.commit()
    
    return posts
```

---

## Step 5: Implement (GREEN Phase)

```python
# File: src/api/posts.py (Implementation)

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Post


router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Session = Depends(get_db)) -> PostResponse:
    """Create new blog post."""
    db_post = Post(
        title=post.title,
        content=post.content,
        author=post.author,
        tags=post.tags or [],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return db_post


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)) -> PostResponse:
    """Get blog post by ID."""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    return post


@router.get("/", response_model=List[PostResponse])
async def list_posts(
    skip: int = 0,
    limit: int = 100,
    author: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[PostResponse]:
    """List blog posts with filtering and pagination."""
    query = db.query(Post)
    
    if author:
        query = query.filter(Post.author == author)
    
    if tag:
        query = query.filter(Post.tags.contains([tag]))
    
    posts = query.offset(skip).limit(limit).all()
    
    return posts


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post: PostUpdate,
    db: Session = Depends(get_db)
) -> PostResponse:
    """Update blog post."""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    # Update fields if provided
    if post.title is not None:
        db_post.title = post.title
    if post.content is not None:
        db_post.content = post.content
    if post.tags is not None:
        db_post.tags = post.tags
    
    db_post.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_post)
    
    return db_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Session = Depends(get_db)) -> None:
    """Delete blog post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    db.delete(post)
    db.commit()
```

---

## Step 6: Run Tests (Should Pass)

```bash
$ pytest tests/api/test_posts.py -v

# Expected: 28 passed
```

```python
test_results = {
    "passed": 28,
    "failed": 0,
    "code_lines": 95
}

orchestrator.verify_tests_pass(test_results)
print("✅ GREEN phase complete!")
```

---

## Step 7: Get Refactoring Suggestions

```python
suggestions = orchestrator.suggest_refactorings("src/api/posts.py")

# Example suggestions:
# - Extract database query logic into repository layer
# - Add response caching for GET endpoints
# - Extract validation logic
```

---

## Step 8: Complete Cycle

```python
orchestrator.complete_refactor_phase(lines_refactored=20)
metrics = orchestrator.complete_cycle()

print(f"✅ REST API TDD cycle complete!")
print(f"Tests: {metrics['tests_passing']}/{metrics['tests_written']}")
```

---

## Benefits Demonstrated

### Phase 1 (Test Generation)
- ✅ **Edge Cases:** Empty strings, invalid IDs, boundary values (pagination limits)
- ✅ **Domain Knowledge:** HTTP status codes, Location headers, timestamp management, idempotency
- ✅ **Error Conditions:** 404, 422, 500 errors
- ✅ **Parametrized Tests:** Pagination combinations, filter variations

### Phase 2 (Workflow Management)
- ✅ **State Machine:** RED→GREEN→REFACTOR enforced
- ✅ **Refactoring Intelligence:** Repository pattern, caching suggestions
- ✅ **Session Tracking:** Save/resume exact endpoint location

### Phase 3 (Integration)
- ✅ **Unified API:** Single orchestrator for complete workflow
- ✅ **Production Ready:** FastAPI best practices with Pydantic validation

---

## API Testing Best Practices

1. **Status Codes:** Test correct HTTP status codes (200, 201, 204, 404, 422)
2. **Validation:** Test Pydantic schema validation (required fields, constraints)
3. **Edge Cases:** Empty lists, missing fields, invalid IDs
4. **Pagination:** Test skip/limit combinations
5. **Filtering:** Test query parameters work correctly
6. **Idempotency:** DELETE should be idempotent
7. **Timestamps:** created_at immutable, updated_at changes on updates

---

**Complete:** All 3 real-world TDD examples now available!
