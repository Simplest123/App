from datetime import datetime

from flask import jsonify, current_app, request, g

from sqlalchemy.orm import joinedload
from Main.database import User, Article, Comment
from Main.utils.response_code import RET
from Main.utils.commons import login_required
from . import index
from .. import db


@index.route('/articles', methods=['GET'])
@login_required
def get_all_articles():
    try:
        articles = db.session.query(Article, User).join(User, Article.user_id == User.user_id).all()
        articles_data = []
        for article, user in articles:
            article_info = {
                'article_id': article.article_id,
                'title': article.title,
                'created_at': article.created_at,
                'show_image': article.show_image,
                'username': user.username,
                'user_id': user.user_id
            }
            articles_data.append(article_info)

        return jsonify(re_code=RET.OK, msg='查询成功', articles=articles_data)

    except Exception as e:
        current_app.logger.error(f'查询失败: {e}')
        return jsonify(re_code=RET.DBERR, msg='查询失败，请联系管理员')


@index.route('/article/<article_id>', methods=['GET'])
@login_required
def get_article(article_id):
    try:
        article = Article.query.get(article_id)
    except Exception as e:
        current_app.logger.error(f'查询失败: {e}')
        return jsonify(re_code=RET.DBERR, msg='查询失败，请联系管理员')

    if not article:
        current_app.logger.error(f'文章不存在')
        return jsonify(re_code=RET.DBERR, msg='文章不存在')

    data = article.to_dict()
    try:
        user = User.query.get(article.user_id)
    except Exception as e:
        current_app.logger.error(f'查询失败: {e}')
        return jsonify(re_code=RET.DBERR, msg='查询失败，请联系管理员')
    if not user:
        current_app.logger.error(f'用户不存在')
        return jsonify(re_code=RET.DBERR, msg='用户不存在')
    article_count = len(user.articles)

    author_info = user.to_dict()
    author_info['article_count'] = article_count

    data['author'] = author_info

    return jsonify(re_code=RET.OK, msg='查询成功', article=data)


@index.route('/article/comments/<article_id>', methods=['GET'])
@login_required
def get_article_comments(article_id):
    try:
        article = Article.query.get(article_id)
        if not article:
            current_app.logger.error(f'文章不存在, article_id: {article_id}')
            return jsonify(re_code=RET.NODATA, msg='文章不存在')

        top_level_comments = (
            Comment.query
            .filter_by(article_id=article_id, parent_id=None)
            .options(joinedload(Comment.user))
            .order_by(Comment.created_at.desc())
            .all()
        )

        all_replies = (
            Comment.query
            .filter(Comment.article_id == article_id, Comment.parent_id.isnot(None))
            .options(joinedload(Comment.user))
            .order_by(Comment.created_at.desc())
            .all()
        )

        def build_comment_tree(comment):
            comment_dict = {
                'comment_id': comment.comment_id,
                'username': comment.user.username,
                'avatar': comment.user.avatar,
                'content': comment.content,
                'created_at': comment.created_at,
                'likes': comment.likes,
                'parent_id': comment.parent_id,
                'replies': []
            }
            return comment_dict

        comments_list = [build_comment_tree(comment) for comment in top_level_comments]

        for reply in all_replies:
            top_level_comment_id = reply.parent_id
            while True:
                parent_comment = next((c for c in all_replies if c.comment_id == top_level_comment_id), None)
                if not parent_comment:
                    break
                top_level_comment_id = parent_comment.parent_id

            for comment in comments_list:
                if comment['comment_id'] == top_level_comment_id:
                    comment['replies'].append(build_comment_tree(reply))
                    break

        return jsonify(re_code=RET.OK, msg='查询成功', comments=comments_list)

    except Exception as e:
        current_app.logger.error(f'查询评论失败, 错误信息: {str(e)}')
        return jsonify(re_code=RET.DBERR, msg='查询评论失败，请联系管理员')


@index.route('/article/comments', methods=['PUT'])
@login_required
def launch_new_comments():
    data = request.get_json()
    if not data:
        current_app.logger.error('评论数据为空')
        return jsonify(re_code=RET.PARAMERR, msg='评论数据不能为空')

    article_id = data.get('article_id')
    content = data.get('content')
    if not article_id or not content:
        current_app.logger.error('参数缺失: article_id 或 content 为空')
        return jsonify(re_code=RET.PARAMERR, msg='文章ID和评论内容不能为空')

    try:
        article = Article.query.get(article_id)
        if not article:
            current_app.logger.error(f'文章不存在, article_id: {article_id}')
            return jsonify(re_code=RET.NODATA, msg='文章不存在')
    except Exception as e:
        current_app.logger.error(f'查询失败, 错误信息: {str(e)}')
        return jsonify(re_code=RET.DBERR, msg='查询失败，请联系管理员')

    try:
        comment = Comment(
            content=content,
            likes=0,
            created_at=datetime.now(),
            article_id=article_id,
            user_id=g.user_id
        )
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f'发表评论失败, 错误信息: {str(e)}')
        db.session.rollback()
        return jsonify(re_code=RET.DBERR, msg='发表评论失败，请稍后重试')

    return jsonify(re_code=RET.OK, msg='发表评论成功')


@index.route('/article/replies', methods=['PUT'])
@login_required
def launch_new_replies():
    data = request.get_json()
    if not data:
        current_app.logger.error('评论数据为空')
        return jsonify(re_code=RET.PARAMERR, msg='评论数据不能为空')

    article_id = data.get('article_id')
    content = data.get('content')
    parent_id = data.get('parent_id')

    if not all([article_id, content, parent_id]):
        current_app.logger.error('参数缺失: article_id、content 或 parent_id 为空')
        return jsonify(re_code=RET.PARAMERR, msg='文章ID、评论内容和父评论ID不能为空')

    try:
        article = Article.query.get(article_id)
        parent_comment = Comment.query.get(parent_id)
        if not article:
            current_app.logger.error(f'文章不存在, article_id: {article_id}')
            return jsonify(re_code=RET.NODATA, msg='文章不存在')
        if not parent_comment:
            current_app.logger.error(f'父评论不存在, parent_id: {parent_id}')
            return jsonify(re_code=RET.NODATA, msg='父评论不存在')
    except Exception as e:
        current_app.logger.error(f'查询失败, 错误信息: {str(e)}')
        return jsonify(re_code=RET.DBERR, msg='查询失败，请联系管理员')

    try:
        comment = Comment(
            content=content,
            likes=0,
            created_at=datetime.now(),
            article_id=article_id,
            user_id=g.user_id,
            parent_id=parent_id
        )
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f'发表回复失败, 错误信息: {str(e)}')
        db.session.rollback()
        return jsonify(re_code=RET.DBERR, msg='发表回复失败，请稍后重试')

    return jsonify(re_code=RET.OK, msg='发表回复成功')


@index.route('/article/likes', methods=['PUT'])
@login_required
def update_likes():
    data = request.get_json()
    if not data:
        current_app.logger.error('评论数据为空')
        return jsonify(re_code=RET.PARAMERR, msg='评论数据不能为空')

    comment_id = data.get('comment_id')
    likes = data.get('likes')

    if not all([comment_id, likes]):
        current_app.logger.error('参数缺失: article_id、content 或 parent_id 为空')
        return jsonify(re_code=RET.PARAMERR, msg='文章ID和点赞数不能为空')

    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            current_app.logger.error(f'评论不存在, parent_id: {comment.comment_id}')
            return jsonify(re_code=RET.NODATA, msg='评论不存在')
    except Exception as e:
        current_app.logger.error(f'查询失败, 错误信息: {str(e)}')
        return jsonify(re_code=RET.DBERR, msg='查询失败，请联系管理员')

    try:
        comment.likes = likes
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f'点赞失败, 错误信息: {str(e)}')
        db.session.rollback()
        return jsonify(re_code=RET.DBERR, msg='点赞失败，请稍后重试')

    return jsonify(re_code=RET.OK, msg='点赞成功')
