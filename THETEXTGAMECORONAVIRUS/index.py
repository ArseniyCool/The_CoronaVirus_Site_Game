from flask import Flask, url_for, request, render_template, make_response, redirect
from data import db_session
from data.users import User
from data.user_sessions import UserSession
from data.friendships import Friendship
from data.games import Game
'Кто бы мог подумать, что все обернется именно так. А ведь так хорошо все было до этого рокового дня...'


class TextQuest:
    def __init__(self):
        self.text1 = '''Я бежал. Без оглядки. Не думая ни о чем. Крис бежал позади, а еще позади те самые незванные гости
захотевшие пообедать человеченкой. Когда я уже почти падал с ног от часового бега, я вдруг подумал, нужен ли мне лишний 
груз в руках в виде старой и дряхлой двустволки. Без патронов. Тем не менее на был дорога мне, 
столько раз она спасала мне жизнь, а я с ней даже не попрощаюсь. А может, сегодня день, когда она мне вновь
спасет жизнь?'''
        self.text2_1 = '''Я решил расстаться со своим дробовиком.. И правильно сделал. Сбросив лишний вес, я ускорился
и почувствовал прилив сил. Пробежав еще несколько минут мне удалось оторваться от мутантов на повороте. Я тихонько поднялся по аварийной
лестнице на крышу какой-то 5 этажки и внезапно понял, что больше бежать я не смогу. Благо на ней гостей не было. Я был один вместе
со своей собакой. Крис поспел за мной, и как будто знал, что мы скрываемся, и потому не издавал не единого звука: в здании
вполне могли быть зомби и поэтому нужно вести себя очень аккуратно.Осмотревшись, я не поверил своим глазам. 
Как от частного дома дяди Эрна я добежал аж до квартала старых трущоб. Ух, я явно должен отдохнуть после бурной ночки.. А быть может
стоит дождаться рассвета?'''
        self.text2_2 = '''Я приберег двустволку.. Ей богу, точно ведь на следующее утро найду патроны и буду жалеть что избавился от нее.
Однако сил становилось все меньше. Пробежав еще пару десятков метров я окончательно выдохся и упал на землю. Крис подошел ко мне и жалобно заскулил
Тем временем зомби были от меня в 2 минутах. Я упал на самой дороге, где некогда разъезжали легковушки. Но я не хотел умирать. Мне в голову пришло
две неплохие идеи. Я мог доплестись к хорошо знакомой мне пятероче, где насколько я помню, можно запереть дверь изнутри. А ведь не факт, что внутри зомби нет
Во-вторых я подумал, что смог бы забраться в подвал хрущевки в 20 метрах. Его я увидел только что, и вообще черт знает что меня там может ждать
'''
        self.answer1 = ['Бросить ружье', 'Продолжать бег']
        self.answer2_1 = ['Лечь спать (Продолжение следует)', 'Ждать рассвета (Продолжение следует)']
        self.answer2_2 = ['Плести к 5-чке (Продолжение следует)', 'Идти в подвал (Продолжение следует)']
        self.step = -1
        self.text_massive = [[self.text1], [self.text2_1, self.text2_2]]

        self.answer_massive = [[self.answer1], [self.answer2_1, self.answer2_2]]

    def render(self):
        pass

    def text_play(self, step_answer=0):
        self.step += 1
        return self.text_massive[self.step][step_answer - 1]

    def answer_play(self, step_answer=0):
        return self.answer_massive[self.step][step_answer - 1]





text_quest = TextQuest()
db_session.global_init("db/development.db")
db_sess = db_session.create_session()

app = Flask(__name__)

visits_count = 0


def check_if_user_signed_in(cookies, db_sess):
    return User.check_cookies(cookies, db_sess)


@app.route("/sign_in_user", methods=['POST'])
def sign_in_user():
    global visits_count
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if current_user:
        return redirect("/users/site")
    else:
        res = User.authenticate_user(request.form["login"], request.form["password"], db_sess)
        user = res[0]
        user_session = res[1]
        if None == user:
            return redirect("/sign_in/user_not_found")
        else:
            res = make_response(redirect("/"))
            res.set_cookie("user_secret", str(user_session.value),
                           max_age=60 * 60 * 24 * 365 * 2)
            return res

@app.route('/')
def landing():
    return redirect("/sign_in/введите пароль")

@app.route("/sign_in/<status>")
def sign_in(status):
    param = {
        "status": status
    }
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if current_user:
        return redirect("/users/site")
    else:
        param['yousername'] = "Ученик Яндекс.Лицея"
        param['title'] = 'TheCoronavirusGame.ru'
        param["array"] = [1, 2, 3, 4, 5]
        param["array_length"] = len(param["array"])
    return render_template('index.html', **param)


@app.route('/sign_up')
def sign_up():
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if current_user:
        return redirect("/users/site")

    param = {}
    return render_template('sign_up.html', **param)


@app.route("/sign_up_user", methods=["post"])
def sign_up_user():
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if current_user:
        return redirect("/users/site")

    res = User.create(request.form["name"], request.form["login"], request.form["password"], db_sess)
    print(res)
    user = res[0]
    user_session = res[1]

    http_res = make_response(redirect("/"))
    http_res.set_cookie("user_secret", str(user_session.value),
                   max_age=60 * 60 * 24 * 365 * 2)
    return http_res


@app.route("/users/game")
def game():
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if not current_user:
        return redirect("/")

    # g = Game.get_last_game(current_user, db_sess)
    # your_mode = "X"
    # if g.user_1_id != current_user.id:
    #     your_mode = "0"
    params = {
        "current_user": current_user,
        "text": text_quest.text_play(),
        "answers": text_quest.answer_play(),
    }

    return render_template("game.html", **params)

@app.route("/users/text_render",  methods=["post"])
def text_render():
    current_user = check_if_user_signed_in(request.cookies, db_sess)

    # g = Game.get_last_game(current_user, db_sess)
    # your_mode = "X"
    # if g.user_1_id != current_user.id:
    #     your_mode = "0"
    answer = int(request.form["radio"])
    print(answer)
    params = {
        "current_user": current_user,
        "text": text_quest.text_play(answer),
        "answers": text_quest.answer_play(answer)
    }

    return render_template("game.html", **params)


@app.route("/users/site")
def site():
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    print(current_user)
    if not current_user:
        return redirect("/")

    g = Game.get_last_game(current_user, db_sess)
    your_mode = "X"
    if g.user_1_id != current_user.id:
        your_mode = "0"
    params = {
        "current_user": current_user,
        "game_in_html": g.to_html(current_user),
        "user_1": User.find_by_id(g.user_1_id, db_sess),
        "user_2": User.find_by_id(g.user_2_id, db_sess),
        "your_mode": your_mode
    }

    return render_template("site.html", **params)

@app.route("/users/scoreboard")
def scoreboard():
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if not current_user:
        return redirect("/")
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    params = {
        "users": User.all(db_sess),
        "current_user": current_user
    }
    return render_template("scoreboard.html", **params)


@app.route("/users/account")
def account():
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if not current_user:
        return redirect("/sign_in/нужно войти в аккаунт")
    params = {
        "users": map(lambda x: User.friendship_asked(x, db_sess), current_user.friends(db_sess)),
        "current_user": current_user
    }
    return render_template("account.html", **params)

@app.route("/users/add_user/<user_id>")
def friend_user(user_id):
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if not current_user:
        return redirect("/sign_in/для добавления в друзья нужно войти")

    user = User.find_by_id(user_id, db_sess)

    Friendship.create_friendship(current_user, user, db_sess)

    params = {
        "users": map(lambda x: User.friendship_asked(x, db_sess), current_user.friends(db_sess)),
        "current_user": current_user
    }
    return render_template("account.html", **params)


@app.route("/users/sign_out")
def sign_out():
    current_user = UserSession.sign_out(request.cookies, db_sess)
    return redirect("/")



if __name__ == '__main__':
    app.run(port=8082, host='127.0.0.1')