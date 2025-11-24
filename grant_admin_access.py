#!/usr/bin/env python
"""
Script to grant admin access to a user
Usage: python grant_admin_access.py username
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sunsavvy.settings')
django.setup()

from django.contrib.auth.models import User

def grant_admin_access(username):
    try:
        user = User.objects.get(username=username)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"SUCCESS! User '{username}' now has admin access.")
        print(f"  - is_staff: {user.is_staff}")
        print(f"  - is_superuser: {user.is_superuser}")
        print(f"  - is_active: {user.is_active}")
        print(f"\nYou can now log in to Django admin at: http://127.0.0.1:8000/admin/")
    except User.DoesNotExist:
        print(f"ERROR: User '{username}' not found.")
        print(f"  Available users: {', '.join(User.objects.values_list('username', flat=True))}")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = 'naved'  # Default to 'naved'
    
    grant_admin_access(username)

