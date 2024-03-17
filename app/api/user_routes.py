from flask import Blueprint, jsonify, render_template, redirect, request
from flask_login import login_required, current_user
from app.models import User, Album, db
from app.forms import CreateAlbumForm
from .aws_helpers import upload_file_to_s3, get_unique_filename

user_routes = Blueprint('users', __name__)


@user_routes.route('/')
@login_required
def users():
    """
    Query for all users and returns them in a list of user dictionaries
    """
    users = User.query.all()
    return {'users': [user.to_dict() for user in users]}


@user_routes.route('/<int:id>')
@login_required
def user(id):
    """
    Query for a user by id and returns that user in a dictionary
    """
    user = User.query.get(id)
    return user.to_dict()


@user_routes.route("/current/albums", methods=["GET","POST"])
@login_required
def createAlbum():
    form = CreateAlbumForm()
    form['csrf_token'].data = request.cookies['csrf_token']
    user = current_user.to_dict()
    # print(user)
    
    if form.validate_on_submit():
        cover_img = form.cover_img.data
        print(cover_img)
        cover_img.filename = get_unique_filename(cover_img.filename)
        upload = upload_file_to_s3(cover_img)
        print(upload)
        
        if "url" not in upload:
            # return render_template("create_album_form.html", form=form, errors=[upload])
            return form.errors
        url = upload["url"]
        new_album = Album(
            name = form.name.data,
            cover_img = url,
            artist_id = user["id"]
            )
        db.session.add(new_album)
        db.session.commit()
        # return redirect("/api/albums")
        return new_album.to_dict()
    if form.errors:
        print(form.errors)
        # return render_template("create_album_form.html", form=form, errors=form.errors)
        return form.errors
    # return render_template("create_album_form.html", form=form, errors=None)
