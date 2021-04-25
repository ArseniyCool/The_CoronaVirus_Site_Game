import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from data.users import User
import json

game_size = 20
class Game(SqlAlchemyBase):
    __tablename__ = 'games'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    move_mode = sqlalchemy.Column(sqlalchemy.String,default="X", nullable=True)
    user_1_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    user_2_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    updated_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)


    def to_html(self, current_user):
        content = json.loads(self.content)
        res = "<table>"
        row_index = 0
        col_index = 0

        your_mode = "X"
        if self.user_1_id != current_user.id:
            your_mode = "0"

        for row in content:
            res += "<tr>"
            col_index = 0
            for col in row:
                res += "<td>"
                res += f"<a class='in-game' href='/games/make_move/{col_index}/{row_index}/{your_mode}'>{col}</a>"
                res += "</td>"
                col_index += 1
            row_index += 1
            res += "</tr>"
        res += "</table>"
        # print(content)
        return res

    def make_move(self, row, col, mode, db_sess):
        if self.move_mode != mode:
            return
        content = json.loads(self.content)
        content[row][col] = mode
        self.content = json.dumps(content)

        if self.move_mode == "X":
            self.move_mode = "0"
        else:
            self.move_mode = "X"

        db_sess.add(self)
        db_sess.commit()

    @classmethod
    def get_last_game(cls, user_1, db_sess):
        games = list(db_sess.query(Game).filter((Game.user_1_id == user_1.id)))

        if len(games) == 0:
            games = list(db_sess.query(Game).filter((Game.user_2_id == user_1.id)))
            if len(games) > 0:
                return games[-1]
            else:
                games = list(db_sess.query(Game).filter((Game.user_2_id == None)))
                if len(games) > 0:
                    g = games[-1]
                    g.user_2_id = user_1.id
                    db_sess.add(g)
                    db_sess.commit()
                    return g
                else:
                    return Game.create_game(user_1, db_sess)
        else:
            return games[-1]

    @classmethod
    def create_game(cls, user_1, db_sess):
        g = Game()
        g.user_1_id = user_1.id
        field = []
        for i in range(game_size):
            row = []
            for j in range(game_size):
                row.append("&nbsp;")
            field.append(row)

        content = json.dumps(field)
        g.content = content

        db_sess.add(g)
        db_sess.commit()
        print(content)
        return g
