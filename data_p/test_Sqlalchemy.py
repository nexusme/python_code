from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import aliased
from sqlalchemy import text
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import exists
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import contains_eager
from sqlalchemy import Table, Text

# 1.连接
engine = create_engine('sqlite:///:memory:', echo=True)
# print(engine)

# 2.声明一个映射
# 创建基类
Base = declarative_base()


# 定义映射类 将是我们将此表映射到的类
class User(Base):
    # 至少需要一个__tablename__属性
    __tablename__ = 'users'
    # 并且至少一个Column是主键
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    nickname = Column(String(50))

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (self.name, self.fullname, self.nickname)


# print(User)

# 3.创建模式 表
# 调用该MetaData.create_all()方法
# 将Engine 作为数据库连接的源。首先检查users表是否存在，然后执行实际语句：CREATE TABLE
Base.metadata.create_all(engine)

# 4.创建映射类的实例
# 创建并检查User对象
ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
print('+++++ed_user: ', ed_user)
print('+++++ed_user.name: ', ed_user.name)
print('+++++ed_user.nickname: ', ed_user.nickname)
print('+++++str(ed_user.id): ', str(ed_user.id))

# 5.创建session
# 定义了一个Session类，用作新Session 对象的工厂
Session = sessionmaker(bind=engine)
# 创建引擎时create_engine()，将其连接到Sessionusing configure()：
Session.configure(bind=engine)
# 每当需要与数据库对话时，都实例化一个Session：
# 该Session与启用了SQLite的关联Engine，
# 但尚未打开任何连接。
# 初次使用时，它会从维护的连接池中检索连接 Engine，并一直保留到我们提交所有更改和/或关闭会话对象为止。
session = Session()

# 6.添加和更新对象
# 将其加入session
ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
session.add(ed_user)

# 创建一个新Query对象，该对象加载的实例User
# 通过“”的name属性 过滤 ed，只得到完整行列表中的第一个结果
our_user = session.query(User).filter_by(name='ed').first()
print('+++++our_user: ', our_user)
print('+++++ed_user is our_user: ', ed_user is our_user)

# User使用一次添加更多对象 add_all()
session.add_all([
    User(name='wendy', fullname='Wendy Williams', nickname='windy'),
    User(name='mary', fullname='Mary Contrary', nickname='mary'),
    User(name='fred', fullname='Fred Flintstone', nickname='freddy')])
# Ed的昵称不太好，所以让我们对其进行更改：
ed_user.nickname = 'eddie'
# 修改记录
print('+++++Modified line: ', session.dirty)
# 正在等待处理的对象
print('+++++Pending objects: ', session.new)

# 在 Session发出UPDATE语句的“ED”的绰号变化，以及INSERT三个新语句User我们添加的对象
# 更改刷新到数据库，并提交事务
session.commit()

# 查看Ed的id属性
print('+++++ed_user.id: ', ed_user.id)

# 7.回滚
# 回滚所做修改
ed_user.name = 'Edwardo'
# 添加一个错误用户faker
faker_user = User(name='fakeuser', fullname='Invalid', nickname='12345')
# 加入session
session.add(faker_user)
# 查询session
session.query(User).filter(User.name.in_(['Edwardo', 'fakeuser'])).all()
print('+++++Faker in session: ', session.query(User).filter(User.name.in_(['Edwardo', 'fakeuser'])).all())
# 进行回滚
session.rollback()
session.query(User).filter(User.name.in_(['ed', 'fakeuser'])).all()
print('+++++Session after rollback: ', session.query(User).filter(User.name.in_(['ed', 'fakeuser'])).all())

# 8.查询
for content in session.query(User).order_by(User.id):
    print('+++++Name: ', content.name, '   Full name: ', content.fullname)

# 以python对象输出
for row in session.query(User, User.name).all():
    print('+++++', row.User, row.name)

# 使用label()构造各个列表达式的名称
# 该构造可从任何ColumnElement派生的对象以及映射到一个的任何类属性（例如User.name）
for row in session.query(User.name.label('name_label')).all():
    print('+++++name_label: ', row.name_label)

# 给User指定的名称，假设调用中存在多个实体query()
# 可以使用aliased()控制
user_alias = aliased(User, name='user_alias')
for row in session.query(user_alias, user_alias.name).all():
    print('+++++', row.user_alias)
# 使用Python数组切片，通常与ORDER BY结合使用
for u in session.query(User).order_by(User.id)[1:3]:
    print('+++++', u)

# 过滤结果，这可以通过filter_by()使用关键字参数的来完成 ：
for name, in session.query(User.name). \
        filter_by(fullname='Ed Jones'):
    print('+++++After filter by: ', name)

# 使用filter
for name, in session.query(User.name). \
        filter(User.fullname == 'Ed Jones'):
    print('+++++After filter: ', name)
# 多条件筛选
for user in session.query(User). \
        filter(User.name == 'ed'). \
        filter(User.fullname == 'Ed Jones'):
    print('+++++多条件筛选：', user)

# 9. 通用过滤器运算符
# 模糊查询 关键词LIKE '%三%' AND u_name LIKE '%猫%'

# IN: query.filter(User.name.in_(['ed', 'wendy', 'jack']))
#
#  works with query objects too:
# query.filter(User.name.in_(
#     session.query(User.name).filter(User.name.like('%ed%'))
# ))
#
#  use tuple_() for composite (multi-column) queries
# from sqlalchemy import tuple_
# query.filter(
#     tuple_(User.name, User.nickname).\
#     in_([('ed', 'edsnickname'), ('wendy', 'windy')])
# )

# NOT IN: query.filter(~User.name.in_(['ed', 'wendy', 'jack']))
# and_ or_ from sqlalchemy import and_ /or_

# 10.返回列表和标量
# all()返回整个列表
query = session.query(User).filter(User.name.like('%ed')).order_by(User.id)
print('+++++query all: ', query.all())

# first() 返回第一个结果作为标量：
print('+++++query first: ', query.first())

# one()完全获取所有行，如果结果中不完全是一个对象标识或组合行，则会引发错误。找到多行：
# print('+++++query one: ', query.one())

# scalar()调用该one()方法，并在成功后返回该行的第一列
# query.scalar()

# 11. 使用文本sql
# 使用text构造文字字符串
for user in session.query(User).filter(text("id<224")).order_by(text("id")).all():
    print('+++++user.name', user.name)

# SQL使用冒号指定绑定参数。要指定值，请使用以下params() 方法
print('+++++search through params: ',
      session.query(User).filter(text("id<:value and name=:name")).params(value=224, name='fred').order_by(
          User.id).one())

# text()可以将表示完整语句的构造传递给 from_statement
result = session.query(User).from_statement(text("SELECT * FROM users where name=:name")).params(name='ed').all()
print('+++++from statement:', result)

# 将列表达式作为位置参数传递给 TextClause.columns()方法来实现
# 也可以stmt = text("SELECT id, name, timestamp FROM some_table")
# stmt = stmt.columns(
#             column('id', Integer),
#             column('name', Unicode),
#             column('timestamp', DateTime)
#         )
stmt = text("SELECT name, id, fullname, nickname FROM users where name=:name")
stmt = stmt.columns(User.name, User.id, User.fullname, User.nickname)
print('+++++通过column传参结果：', session.query(User).from_statement(stmt).params(name='ed').all())

# 仍可以指定要返回的列和实体
stmt = text('SELECT name, id FROM users where name=:name')
stmt = stmt.columns(User.name, User.id)
print('+++++返回指定列和实体', session.query(User.id, User.name).from_statement(stmt).params(name='ed').all())

# 12.计数
# Query包括一种方便的计数方法，称为count()
print('+++++count: ', session.query(User).filter(User.name.like('%ed')).count())

# 直接使用func.count()可从func构造中获得 的表达式来指定“计数”功能
# 返回每个不同用户名的计数：
print('+++++count all users: ', session.query(func.count(User.name), User.name).group_by(User.name).all())

# 简化，我们可以将其应用为：SELECT count(*) FROM table
print('+++++简化：', session.query(func.count('*')).select_from(User).all())
print('+++++简化1：', session.query(func.count('*')).select_from(User).scalar())

# 使用主键来表示计数
print('+++++使用主键: ', session.query(func.count(User.id)).scalar())


# 13.建立关系
class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='addresses')

    def __repr__(self):
        return "<Address(email_address= '%s')>" % self.email_address


User.addresses = relationship("Address", order_by=Address.id, back_populates="user")

# addresses在数据库中创建表：
Base.metadata.create_all(engine)

# 14. 处理相关对象
jack = User(name='jack', fullname='Jack Bean', nickname='gjffdd')
jack.addresses = [Address(email_address='jack@google.com'), Address(email_address='j25@yahoo.com')]

print('+++++Jack address: ', jack.addresses)

# 添加并提交到数据库
session.add(jack)
session.commit()
# 查看jack
print('+++++hack,address:', jack.addresses)

# 15.使用链接查询
# 使用Query.filter()将它们的相关列关连起来
for u, a in session.query(User, Address).filter(User.id == Address.user_id).filter(
        Address.email_address == 'jack@google.com').all():
    print('+++++关连过后的表：', u, a)

# 使用以下Query.join()实现SQL JOIN语法
ss_user_join_address = session.query(User).join(Address).filter(Address.email_address == 'jack@google.com').all()
print('+++++使用join(): ', ss_user_join_address)

# 如果没有foreignkey
# query.join(Address, User.id==Address.user_id)    # explicit condition
# query.join(User.addresses)                       # specify relationship from left to right
# query.join(Address, User.addresses)              # same, with explicit target
# query.join('addresses')                          # same, using a string

# outerjoin()功能将相同的想法用于“外部”联接
# query.outerjoin(User.addresses)   # LEFT OUTER JOIN

# 如果ON子句是纯SQL表达式，则该Query.join()方法通常从实体列表中最左边的项开始连接。
# 要控制JOIN列表中的第一个实体，请使用以下Query.select_from()方法：
# query = session.query(User, Address).select_from(Address).join(User)

# 16.使用别名
# 在多个表中查询时，如果同一表需要被多次引用，SQL通常要求该表使用另一个名称作为别名，以便可以与该表的其他出现区分开
# 查找同时拥有两个不同电子邮件地址的用户：
adalias1 = aliased(Address)
adalias2 = aliased(Address)
for username, email1, email2 in session.query(User.name, adalias1.email_address, adalias2.email_address). \
        join(adalias1, User.addresses). \
        join(adalias2, User.addresses). \
        filter(adalias1.email_address == 'jack@google.com'). \
        filter(adalias2.email_address == 'j25@yahoo.com'):
    print('+++++拥有两个不同电子邮件地址的用户：', username, email1, email2)

# 17. 使用子查询
# 加载“User”对象以及每个用户有多少“Address”记录数
# 构造一个statement
stmt1 = session.query(Address.user_id, func.count('*').label('address_count')).subquery()
print('stmt1', stmt1)

print('构造：', session.query(User, stmt1.c.address_count).
      outerjoin(stmt1, User.id == stmt1.c.user_id).order_by(User.id))
# 它的行为就像一个Table构造，例如在本教程开始时为之创建的users构造 。可以通过称为c的属性访问语句上的列：
for u, count in session.query(User, stmt1.c.address_count). \
        outerjoin(stmt1, User.id == stmt1.c.user_id).order_by(User.id):
    print(u, count)

# 18. 从子查询中选择实体
# 子查询映射到实体
stmt11 = session.query(Address).filter(Address.email_address != 'j25@yahoo.com').subquery()
adalias3 = aliased(Address, stmt11)
for user, address in session.query(User, adalias3).join(adalias3, User.addresses):
    print(user)
    print(address)
#
# 使用exist
stmt = exists().where(Address.user_id == User.id)
for name, in session.query(User.name).filter(stmt):
    print('+++++使用exist：', name)

# 该查询具有几个运算符，这些运算符可自动使用EXISTS。
# 在上面，可以使用any（）沿着User.addresses关系来表示语句
for name, in session.query(User.name).filter(User.addresses.any()):
    print('+++++使用any: ', name)
# any() 也可限制匹配的行：
for name, in session.query(User.name).filter(User.addresses.any(Address.email_address.like('%google%'))):
    print('+++++Use any to limit: ', name)

# has与any相似
print('+++++使用has：', session.query(Address).filter(Address.user.has(User.name == 'jack')).all())

# 19.预加载
# selectin加载
jack = session.query(User).options(selectinload(User.addresses)).filter_by(name='jack').one()
print('+++++selectin jack: ', jack)
print('+++++selectin jacks address', jack.addresses)
# joined加载
jack = session.query(User).options(joinedload(User.addresses)).filter_by(name='jack').one()
print('+++++joined jack: ', jack)
print('+++++joined jacks address', jack.addresses)
# Explicit Join + Eagerload
jack_address = session.query(Address).join(Address.user).filter(User.name == 'jack').options(
    contains_eager(Address.user)).all()
print('+++++Explicit Join jack: ', jack_address)
print('+++++Explicit Join address', jack_address[0].user)
# 20. 删除
session.delete(jack)
print('+++++jack after deleting: ', session.query(User).filter_by(name='jack').count())
session.close()
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    fullname = Column(String)
    nickname = Column(String)

    addresses = relationship("Address", back_populates='user',
                             cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
            self.name, self.fullname, self.nickname)


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return "<Address(email_address='%s')>" % self.email_address


# 通过主键加载jack
jack = session.query(User).get(5)
# 移除一条Address
del jack.addresses[1]
print('+++++remove one address: ', session.query(Address).filter(
    Address.email_address.in_(['jack@google.com', 'j25@yahoo.com'])
).count())

# 删除杰克将同时删除杰克和Address与用户相关联的其余人：
session.delete(jack)
print('+++++delete jack: ', session.query(User).filter_by(name='jack').count())
print('+++++after delete: ', session.query(Address).filter(
    Address.email_address.in_(['jack@google.com', 'j25@yahoo.com'])
).count())

# 21. 建立多对多关系
# 创建一个未映射的Table
post_keywords = Table('post_keywords', Base.metadata,
                      Column('post_id', ForeignKey('posts.id'), primary_key=True),
                      Column('keyword_id', ForeignKey('keywords.id'), primary_key=True)
                      )


# 使用互补构造定义BlogPost和Keyword， relationship()每个构造都将post_keywords 表称为关联表：
class BlogPost(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    headline = Column(String(255), nullable=False)
    body = Column(Text)

    # many to many BlogPost<->Keyword
    keywords = relationship('Keyword',
                            secondary=post_keywords,
                            back_populates='posts')

    def __init__(self, headline, body, author):
        self.author = author
        self.headline = headline
        self.body = body

    def __repr__(self):
        return "BlogPost(%r, %r, %r)" % (self.headline, self.body, self.author)


class Keyword(Base):
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key=True)
    keyword = Column(String(50), nullable=False, unique=True)
    posts = relationship('BlogPost',
                         secondary=post_keywords,
                         back_populates='keywords')

    def __init__(self, keyword):
        self.keyword = keyword


# 访问时 User.posts，我们希望能够进一步过滤结果，以免加载整个集合。为此，我们使用所接受的设置 relationship()叫lazy='dynamic'
BlogPost.author = relationship(User, back_populates="posts")
User.posts = relationship(BlogPost, back_populates="author", lazy="dynamic")
# 创建新表
Base.metadata.create_all(engine)
# 填入数据
wendy = session.query(User). \
    filter_by(name='wendy'). \
    one()
post = BlogPost("Wendy's Blog Post", "This is a test", wendy)
session.add(post)

# 将关键字唯一地存储在数据库中，创建关键字：
post.keywords.append(Keyword('wendy'))
post.keywords.append(Keyword('firstpost'))

# 使用关键字“ firstpost”查找所有博客文章。
# 使用 any运算符查找“博客帖子中任何关键字具有关键字字符串'firstpost'的博客
print('+++++查找关键词firstpost： ', session.query(BlogPost).filter(BlogPost.keywords.any(keyword='firstpost')).all())

# 查找用户wendy拥有的帖子，则可以缩小为User以此作为父对象：


print('+++++缩小到用户之后的结果：', session.query(BlogPost).
      filter(BlogPost.author == wendy).
      filter(BlogPost.keywords.any(keyword='firstpost')).
      all())

# 使用Wendy自己的posts关系（一种“动态”关系）直接从那里查询：
print('+++++利用自己的动态关系：', wendy.posts.filter(BlogPost.keywords.any(keyword='firstpost')).all())
