from flask import render_template, flash, redirect, session, url_for, request,\
                  g, jsonify
from flask.ext.login import login_user, logout_user, current_user,\
                            LoginManager,login_required
from app import app, db, lm, weibo, babel
from forms import LoginForm, EditForm, PostForm, SearchForm
from models import User, Post
from datetime import datetime
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, LANGUAGES
from flask.ext.babel import gettext
from guess_language import guessLanguage
from translate import baidu_translate

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())



@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    form = PostForm()
    if g.user.is_authenticated :
        if form.validate_on_submit():
            language = guessLanguage(form.post.data)
            if language == 'UNKNOWN' or len(language) >5:
                language = ''
            post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user, language=language)
            db.session.add(post)
            db.session.commit()
            flash(gettext('Your post is now live!'))
            return redirect(url_for('index'))
        posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
        return render_template('index.html',
                                title='home',
                                form=form,
                                posts=posts)
    else:
        return redirect(url_for('login'))

from werkzeug.utils import secure_filename
import os
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
        f = request.files['file-1']
        fname = f.filename.split('\\')[-1]
        f.save(os.path.join( 'app/static/img/', '1.gif' ))
        return "1"
        return "2"
    return render_template('upload.html')

@app.route('/login')
def login():
    return weibo.authorize(callback=url_for('authorized',
        _external=True))


@app.route('/login/authorized')
def authorized():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    resp = weibo.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    social_id = resp['uid']
    if social_id is None:
        flash('Authentication failed.')
        return "social_id is none"
    #access_token = resp['access_token']
    resp = weibo.get('users/show.json', {'uid' : social_id})
    username = resp.data['screen_name']
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username)
        db.session.add(user)
        db.session.add(user.follow(user))
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('oauth_token', None)
    logout_user()
    return redirect(url_for('index'))


@weibo.tokengetter
def get_weibo_oauth_token():
    return session.get('oauth_token')


def change_weibo_header(uri, headers, body):
    """Since weibo is a rubbish server, it does not follow the standard,
    we need to change the authorization header for it."""
    auth = headers.get('Authorization')
    if auth:
        auth = auth.replace('Bearer', 'OAuth2')
        headers['Authorization'] = auth
    return uri, headers, body

weibo.pre_request = change_weibo_header

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = get_locale()

@app.route('/search', methods=['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit:
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
                            query=query,
                            results=results)


@app.route('/user/<social_id>')
@app.route('/user/<social_id>/<int:page>')
@login_required
def user(social_id, page=1):
    user = User.query.filter_by(social_id=social_id).first()
    if user == None:
        flash('User %s not found.')
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
                           user=user,
                           posts=posts)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash(gettext('Your changes have been saved.'))
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)

@app.route('/follow/<social_id>')
@login_required
def follow(social_id):
    user = User.query.filter_by(social_id=social_id).first()
    if user is None:
        flash('User %s not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', social_id=social_id))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow' + user.nickname + '!')
        return redirect(url_for('user', social_id=social_id))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + user.nickname + '!')
    return redirect(url_for('user', social_id=social_id))

@app.route('/unfollow/<social_id>')
@login_required
def unfollow(social_id):
    user = User.query.filter_by(social_id=social_id).first()
    if suer is None:
        flash('User %s not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', social_id=social_id))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow' + user.nickname + '!')
        return redirect(url_for('user', social_id=social_id))
    db.session.add(u)
    db.session.commit()
    flash('You are now unfollowing' + user.nickname + '!')
    return redirect(url_for('user', social_id=social_id))


@app.route('/translate', methods=['POST'])
@login_required
def translate():
    return jsonify({
        'text': baidu_translate(
            request.form['test'],
            request.form['sourceLang'],
            reqsuet.form['destLang']
        )
    })

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    if post is None:
        flash(gettext('Post not found.'))
        return redirect(url_for('index'))
    if post.user_id != g.user.id:
        flash(gettext('You cannot delete this post.'))
        return redirect(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    flash(gettext('The post has been deleted!'))
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('400.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
