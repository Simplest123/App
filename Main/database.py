from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

from Main import db


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    phone = db.Column(db.String(20), unique=True, nullable=False, comment='电话')
    email = db.Column(db.String(50), unique=True, nullable=False, comment='邮箱')
    username = db.Column(db.String(20), unique=True, nullable=False, comment='用户名')
    password = db.Column(db.String(200), nullable=False, comment='密码（密文）')
    gender = db.Column(db.String(2), default="男", index=True, comment='性别')
    birth_day = db.Column(db.String(30), default=lambda: date.today().strftime('%Y-%m-%d %H:%M:%S'), comment='生日')
    career = db.Column(db.String(30), comment='职业')
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='注册时间')
    avatar = db.Column(db.String(150), default='https://remote-sensing-system.oss-cn-beijing.aliyuncs.com/images/default%20avatar.jpg', comment='头像')
    real_name = db.Column(db.String(20), comment='实名')
    id_card = db.Column(db.String(25), comment='身份证')

    actions = db.relationship('Action', back_populates='user', cascade='all, delete-orphan')
    projects = db.relationship('Project', back_populates='user', cascade='all, delete-orphan')
    articles = db.relationship('Article', back_populates='user', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')

    @property
    def password_hash(self):
        raise AttributeError('')

    @password_hash.setter
    def password_hash(self, password):
        self.password = generate_password_hash(password, method='scrypt')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        user_info = {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'gender': self.gender,
            'birthday': self.birth_day,
            'real_name': self.real_name,
            'id_card': self.id_card,
            'career': self.career,
            'created_at': self.created_at,
            'avatar': self.avatar,
        }
        return user_info

    def to_auth_dict(self):
        """real name authentication"""
        return {
            'real_name': self.real_name,
            'id_card': self.id_card
        }


class Action(db.Model):
    __tablename__ = 'action'
    action_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='行为ID')
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='详细信息')
    type = db.Column(db.String(10), comment='类别')
    description = db.Column(db.String(50), comment='详细信息')

    user = db.relationship('User', back_populates='actions')

    def to_dict(self):
        action = {
            'timestamp': self.timestamp,
            'type': self.type,
            'description': self.description
        }
        return action


class Project(db.Model):
    __tablename__ = 'project'
    project_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='项目ID')
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    project_name = db.Column(db.String(100), unique=True, nullable=False, comment='项目名称')
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='注册时间')

    scenario = db.Column(db.String(20), nullable=False, comment='项目场景')
    scale = db.Column(db.String(5), nullable=False, default='小', comment='项目场景')
    detection_classes = db.Column(db.JSON, nullable=False, comment='检测类别列表')
    conf_threshold = db.Column(db.Float, default=0.3, comment='置信度阈值')
    source_path = db.Column(db.String(200), nullable=False, comment='源文件路径')
    result_path = db.Column(db.String(200), comment='结果文件路径')

    user = db.relationship('User', back_populates='projects')
    data = db.relationship('DetectionData', back_populates='project', cascade='all, delete-orphan')


class DetectionData(db.Model):
    """
    results:
    {
        ob_counts
        consumption_time
        objects: {
            object: {coordinates: [x_min, y_min, x_max, y_max]
                    cls
                    conf
            }
        }
    }
    """
    __tablename__ = 'detection_data'
    data_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='数据ID')
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id', ondelete='CASCADE'), nullable=False)
    results = db.Column(db.JSON, nullable=False, comment='检测结果')

    project = db.relationship('Project', back_populates='data')


class Article(db.Model):
    __tablename__ = 'article'
    article_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='文章ID')
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    abstract = db.Column(db.Text, nullable=False, comment='摘要')
    title = db.Column(db.String(100), nullable=False, comment='标题')
    content = db.Column(db.Text, nullable=False, comment='内容')
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='启动时间')
    show_image = db.Column(db.String(150), comment='展示图片')

    thumbs_up = db.Column(db.Integer, comment='点赞')
    collect = db.Column(db.Integer, comment='收藏')

    user = db.relationship('User', back_populates='articles')
    comments = db.relationship('Comment', back_populates='article', cascade='all, delete-orphan')

    def to_dict(self):
        article = {
            'abstract': self.abstract,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at,
            'show_image': self.show_image,
        }
        return article


class Comment(db.Model):
    __tablename__ = 'comment'
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='评论ID')
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.article_id', ondelete='CASCADE'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.comment_id'), comment='父评论ID')

    content = db.Column(db.Text, nullable=False, comment='内容')
    likes = db.Column(db.Integer, default=0, comment='点赞数')
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment='发布时间')

    # 关系定义
    user = db.relationship('User', back_populates='comments')
    article = db.relationship('Article', back_populates='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[comment_id]))

    def to_dict(self):
        return {
            'comment_id': self.comment_id,
            'content': self.content,
            'likes': self.likes,
            'created_at': self.created_at
        }
