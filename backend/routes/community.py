"""
Community forum routes for Sakhi App
"""

from fastapi import APIRouter, HTTPException
from typing import List
from models import PostCreate, Post, CommentCreate, Comment, MessageResponse
from database import db
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.translation_service import translation_service

router = APIRouter()

@router.post("/posts", response_model=MessageResponse)
async def create_post(user_id: int, post: PostCreate):
    """Create a new community post"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        # Generate anonymous name if anonymous posting
        anonymous_name = None
        if post.anonymous:
            anonymous_name = f"User{user_id:04d}"

        cursor.execute(
            '''INSERT INTO posts (user_id, content, language, anonymous_name, upvotes)
               VALUES (?, ?, ?, ?, 0)''',
            (user_id, post.content, post.language, anonymous_name)
        )
        conn.commit()
        post_id = cursor.lastrowid
        conn.close()

        return MessageResponse(message=f"Post created with ID: {post_id}")

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts")
async def get_posts(user_lang: str = 'en', limit: int = 20):
    """Get all community posts with translation if needed"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''SELECT p.*, u.name as author_name
           FROM posts p
           LEFT JOIN users u ON p.user_id = u.id
           ORDER BY p.created_at DESC LIMIT ?''',
        (limit,)
    )
    posts = cursor.fetchall()
    conn.close()

    # Translate posts if user's language differs
    translated_posts = []
    for post in posts:
        post_dict = dict(post)
        post_dict['translated'] = False

        # Set display name: use anonymous_name if exists, otherwise use author_name
        if post_dict.get('anonymous_name'):
            post_dict['display_name'] = post_dict['anonymous_name']
        else:
            post_dict['display_name'] = post_dict.get('author_name', 'Anonymous')

        # Only translate if languages differ
        if translation_service.should_translate(user_lang, post_dict['language']):
            try:
                post_dict['content'] = await translation_service.translate_dynamic_content(
                    post_dict['content'],
                    post_dict['language'],
                    user_lang
                )
                post_dict['translated'] = True
            except Exception as e:
                print(f"Translation error: {e}")

        translated_posts.append(post_dict)

    return translated_posts

@router.get("/posts/{post_id}")
async def get_post(post_id: int, user_lang: str = 'en'):
    """Get a specific post by ID"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()
    conn.close()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post_dict = dict(post)
    post_dict['translated'] = False

    # Translate if needed
    if translation_service.should_translate(user_lang, post_dict['language']):
        try:
            post_dict['content'] = await translation_service.translate_dynamic_content(
                post_dict['content'],
                post_dict['language'],
                user_lang
            )
            post_dict['translated'] = True
        except Exception as e:
            print(f"Translation error: {e}")

    return post_dict

@router.post("/posts/{post_id}/upvote")
async def upvote_post(post_id: int, user_id: int):
    """Upvote a post"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        # Check if user already upvoted
        cursor.execute(
            'SELECT * FROM post_upvotes WHERE post_id = ? AND user_id = ?',
            (post_id, user_id)
        )
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Already upvoted")

        # Add upvote
        cursor.execute(
            'INSERT INTO post_upvotes (post_id, user_id) VALUES (?, ?)',
            (post_id, user_id)
        )

        # Increment upvote count
        cursor.execute(
            'UPDATE posts SET upvotes = upvotes + 1 WHERE id = ?',
            (post_id,)
        )

        conn.commit()
        conn.close()

        return MessageResponse(message="Post upvoted successfully")

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/comments", response_model=MessageResponse)
async def create_comment(post_id: int, user_id: int, comment: CommentCreate):
    """Add a comment to a post"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''INSERT INTO comments (post_id, user_id, content, language)
               VALUES (?, ?, ?, ?)''',
            (post_id, user_id, comment.content, comment.language)
        )
        conn.commit()
        comment_id = cursor.lastrowid
        conn.close()

        return MessageResponse(message=f"Comment added with ID: {comment_id}")

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}/comments")
async def get_comments(post_id: int, user_lang: str = 'en'):
    """Get all comments for a post"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''SELECT c.*, u.name as author_name
           FROM comments c
           LEFT JOIN users u ON c.user_id = u.id
           WHERE c.post_id = ?
           ORDER BY c.created_at ASC''',
        (post_id,)
    )
    comments = cursor.fetchall()
    conn.close()

    # Translate comments if needed
    translated_comments = []
    for comment in comments:
        comment_dict = dict(comment)

        if translation_service.should_translate(user_lang, comment_dict['language']):
            try:
                comment_dict['content'] = await translation_service.translate_dynamic_content(
                    comment_dict['content'],
                    comment_dict['language'],
                    user_lang
                )
            except Exception as e:
                print(f"Translation error: {e}")

        translated_comments.append(comment_dict)

    return translated_comments

@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, user_id: int):
    """Delete a post"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM posts WHERE id = ? AND user_id = ?', (post_id, user_id))
    conn.commit()
    conn.close()

    return MessageResponse(message="Post deleted successfully")
