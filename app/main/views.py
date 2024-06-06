from flask import render_template, redirect, url_for, abort, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import Role, User
from ..decorators import admin_required
from sqlalchemy import text
from .updata import update_chart_data
from json import loads
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/kokeilu')
@login_required
def malli():
    return render_template('esimerkki.html')

@main.route('/user/<username>')
def user(username):
    # Huom. user.html:ssä user.last_seen ilmaisee ping-metodilla annetun ajan,
    # eikä tietokantaan tallennettua aikaa.
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        # user.email = form.email.data
        # user.username = form.username.data
        # user.confirmed = form.confirmed.data
        # user.role = Role.query.get(form.role.data)
        # user.name = form.name.data
        # user.location = form.location.data
        # user.about_me = form.about_me.data
        form.role.data = Role.query.get(form.role.data)
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    # form.email.data = user.email
    # form.username.data = user.username
    # form.confirmed.data = user.confirmed
    # form.role.data = user.role_id
    # form.name.data = user.name
    # form.location.data = user.location
    # form.about_me.data = user.about_me
    
    # Huom. role_id ei häiritse, eikä sitä tarvita select-optioiden listaamiseen
    form = EditProfileAdminForm(user=user,obj=user)
    return render_template('edit_profile.html', form=form, user=user)

@main.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    # users = User.query.all() 
    if request.form.get('painike'):
        users = request.form.getlist('users')
        if len(users) > 0:
            query_start = "INSERT INTO users (id,active) VALUES "
            query_end = " ON DUPLICATE KEY UPDATE active = VALUES(active)"
            query_values = ""
            active = request.form.getlist('active')
            for v in users:
                if v in active:
                    query_values += "("+v+",1),"
                else:
                    query_values += "("+v+",0),"
            query_values = query_values[:-1]
            query = query_start + query_values + query_end
            print("\n"+query+"\n")
            '''INSERT INTO users (id,active) VALUES (6,1),(7,1) 
               ON DUPLICATE KEY UPDATE active = VALUES(active)
            '''
            # result = db.session.execute('SELECT * FROM my_table WHERE my_column = :val', {'val': 5})
            db.session.execute(text(query))
            db.session.commit()
            # return query
            #return str(request.form.getlist('users')) + \
            #       "<br>" + \
            #        str(request.form.getlist('active'))
        else:
            flash("Käyttäjälista puuttuu.")
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.name).paginate(
        page=page, per_page=current_app.config['SOVELLUSMALLI_POSTS_PER_PAGE'],
        error_out=False)
    lista = pagination.items
    return render_template('users.html',users=lista,pagination=pagination,page=page)

@main.route('/poista', methods=['GET', 'POST'])
@login_required
@admin_required
def poista():
    # print("POISTA:"+request.form.get('id'))
    user = User.query.get(request.form.get('id'))
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        flash(f"Käyttäjä {user.name} on poistettu")
        return jsonify(OK="käyttäjä on poistettu.")
    else:
        return jsonify(virhe="käyttäjää ei löydy.")
    
@main.route('/update_chart_data', methods=['GET'])
def update_data():
    update_chart_data()
    return "OK"

@main.route('/get_chart_data', methods=['GET'])
def get_data():
  select_query = text('SELECT * FROM chart_data WHERE id = :id')
  result = db.session.execute(select_query, {"id": 0})
  return jsonify(loads(list(result)[0][1]))