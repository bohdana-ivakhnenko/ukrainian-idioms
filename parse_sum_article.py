import json
import csv
from bs4 import BeautifulSoup


def collect_article(paragraph, dirty):
    diam = False
    illus = False
    citation = False
    explanation_next = False

    idiom = ""
    pieces = []
    illustration = {"citation": "",
                    "source": ""}
    illustrations = []
    phrases = []

    if not dirty:
        for index, child in enumerate(paragraph.children):
            print()

            string = child.text.strip(" \n—.").replace("\n", " ")
            if diam:
                if '<span class="s">' in str(child):
                    citation = True
                    illustration["source"] = string
                    illustrations.append(illustration)
                    illustration = {"citation": "",
                                    "source": ""}
                if '<i class="illus">' in str(child):
                    print("here def - ", pieces)
                    illus = True
                    illustration["citation"] = string
                    explanation_next = False
                if explanation_next and not (illus or citation or
                                             '<span class="z">' in str(list(paragraph.children)[index])):
                    pieces.append(string)
                if '<span class="z">' in str(child):
                    if pieces and ((illus and citation)
                                   or '<span class="z">' in str(list(paragraph.children)[index])
                                   or index + 1 == len(list(paragraph.children))):
                        phrase = {"idiom": idiom,
                                  "definition": "".join(pieces),
                                  "illustrations": illustrations.copy()}
                        phrases.append(phrase)
                        print("phrase: \n", phrase)
                        idiom = ""
                        pieces.clear()
                        illustrations.clear()
                        illus = False
                        citation = False
                        explanation_next = False

                    idiom = string
                    explanation_next = True
            elif not diam and child.text == "♦":
                diam = True

        phrase = {"idiom": idiom,
                  "definition": "".join(pieces),
                  "illustrations": illustrations.copy()}
        phrases.append(phrase)

        return phrases

    else:
        second_def = False

        for index, child in enumerate(paragraph.children):
            string = child.text.strip(" \n—.").replace("\n", " ")

            if diam:
                if '<span class="s">' in str(child) or \
                        index in [len(list(paragraph.children))-1, len(list(paragraph.children))-2] \
                        or (pieces and '<span class="z">' in str(list(paragraph.children)[index+1])):
                    print("illustration - ", string)
                    illustration["source"] = string
                    illustrations.append(illustration)
                    explanation_next = False

                    if second_def or index in [len(list(paragraph.children))-1, len(list(paragraph.children))-2]:
                        phrase = {"idiom": idiom,
                                  "definition": "".join(pieces),
                                  "illustrations": illustrations}
                        phrases.append(phrase)
                        print("SECOND phrase - ", phrase)
                        break

                if illustrations and '<span class="z">' in str(child):
                    second_def = True
                    phrase = {"idiom": idiom,
                              "definition": "".join(pieces),
                              "illustrations": illustrations}
                    phrases.append(phrase)
                    print("phrase - ", phrase)
                    idiom = str
                    pieces = []
                    illustration = {"citation": "",
                                    "source": ""}
                    illustrations = []

                if explanation_next and not citation:
                    pieces.append(string)
                    print("PIECE - ", string)

                if '<span class="z">' in str(child):
                    idiom = string
                    explanation_next = True
                    print("IDIOM - ", idiom)
                    print("citation - ", citation)
                    # diam = False

            elif not diam and child.text == "♦":
                diam = True

        print("phrases:\n", *phrases)
        return phrases


def parse(text):
    article = BeautifulSoup(text, features="html.parser")

    if article.find("i", {"class", "illus"}):
        dirty = False
    else:
        dirty = True
    print("dirty:", dirty)

    if article.find("p", {"class", "znach"}):
        paragraphs = [article.find("p", {"class", "znach"})]
        paragraphs.extend(paragraphs[0].findAllNext("p", {"class", "znach"}))
    elif article.find("p"):
        paragraphs = [article.find("p")]
    else:
        print("Other problem")
        # paragraphs = [article.find("p")]
        # print("paragraphs - ", paragraphs)
        return

    print("paragraphs: ", len(paragraphs), "\n", paragraphs)

    idioms = []
    for paragraph in paragraphs:
        if paragraph.find("span", {"class", "diam"}) and not dirty:
            idioms_ = collect_article(paragraph, dirty)
            idioms.extend(idioms_)
    return idioms


with open("idioms_articles_sum.json", "r", encoding="utf-8") as file:
    dictionary = json.loads(file.read())

lines = [("idiom", "definition", "citation", "source")]

for letter, articles in tuple(dictionary.items()):
    for word, definition in tuple(articles.items()):
        print(word)
        idioms = parse(definition)
        if idioms:
            for idiom in idioms:
                if idiom['illustrations']:
                    lines.append((idiom['idiom'], idiom['definition'],
                                  idiom['illustrations'][0]['citation'],
                                  idiom['illustrations'][0]['source']))
                else:
                    lines.append((idiom['idiom'], idiom['definition'], None, None))
        print()

with open("idioms_sum_table.tsv", "w", encoding="utf-8") as file:
    writer = csv.writer(file, delimiter='\t', lineterminator='\n')
    print("lines: \n", *lines)

    for line in lines:
        writer.writerow(line)

with open("idioms_sum_table_to_clean.tsv", "w", encoding="utf-8") as file:
    writer = csv.writer(file, delimiter='\t', lineterminator='\n')
    print("lines: \n", *lines)

    for line in lines:
        writer.writerow(line)


# test_article = """<div itemprop=\"articleBody\"><p><strong class=\"title\" itemprop=\"headline\">КИШЕНЬК<span class=\"stressed\">О</span><span class=\"stress\">́</span>ВИЙ</strong>, а, е. </p><p class=\"znach\"><span class=\"zn\">1.</span> <abbr title=\"стосовний\">Стос.</abbr> до кишені (у 1 знач.).\n<i class=\"illus\">Кишеньковий викрій.</i>\n<br/><span class=\"diam\">♦</span> <span class=\"z\">Кишенькова справа</span> — справа, пов'язана з грішми.\n<i class=\"illus\">Поспішаю заспокоїти вас щодо вашої справи кишенькової</i>\n<span class=\"s\">(Володимир Самійленко, II, 1958, 248)</span>; <span class=\"z\">Кишеньковий злодій</span> — той, хто\nкраде з кишені. <i class=\"illus\">Раз за разом стражники.. підводили\nдо нього то впійманих на гарячому кишенькових злодіїв,\nто всяких зальотних аферисток</i> <span class=\"s\">(Олесь Гончар, Таврія..,\n1957, 56)</span>; <span class=\"z\">Кишенькові витрати</span> — дрібні витрати;\n<span class=\"z\">Кишенькові гроші</span> — гроші на дрібні витрати. <i class=\"illus\">Головне ж\nдля нього.. кишенькові гроші, які.. потрапляли до його\nрук від пестливої матері</i> <span class=\"s\">(Натан Рибак, Час, 1960, 638)</span>.\n</p><p class=\"znach\"><span class=\"zn\">2.</span> Який носять у кишені (у 1 знач.), маленький\nрозміром. <i class=\"illus\">Простягши руку, взяла <span class=\"sq\">[Целя]</span> з круглого\nстолика.. маленький, золотий кишеньковий годинник</i> <span class=\"s\">(Іван Франко,\nII, 1950, 288)</span>; <i class=\"illus\">Микола встав і, присвічуючи собі\nкишеньковим ліхтариком, пішов у темінь вишневого саду</i> <span class=\"s\">(Любомир Дмитерко,\nНаречена, 1959, 230)</span>; <i class=\"illus\">Кишеньковий словник.</i></p></div>"""
# test_article__ = """<div itemprop=\"articleBody\"><p><strong class=\"title\" itemprop=\"headline\">Д<span class=\"stressed\">О</span><span class=\"stress\">́</span>ВГИЙ</strong>, а, е; <abbr class=\"mark\" title=\"вищий ступінь\">вищ. ст.</abbr> довший. </p><p class=\"znach\"><span class=\"zn\">1.</span> Який має велику\nдовжину; протилежне <span class=\"rozb\">короткий</span>. <i class=\"illus\">Дорога там\nдовга й широка</i> <span class=\"s\">(Леся Українка, I, 1951, 20)</span>; <i class=\"illus\">Вона жбурнула геть\nвід себе хустку, відкинула своє довге волосся, що падало\nїй на очі</i> <span class=\"s\">(Олександр Довженко, I, 1958, 245)</span>; <br/><span class=\"tinok\">//</span>  <abbr class=\"mark\" title=\"розмовне\">розм.</abbr> Високий на зріст\n(про людину). <i class=\"illus\">Довгий, сухорлявий о. Мойсей трохи\nскинувсь своєю постаттю.. на тих довгих, темних\nаскетів святих, що малюють на візантійських образах</i>\n<span class=\"s\">(Нечуй-Левицький, I, 1956, 117)</span>.\n</p><p class=\"znach\"><span class=\"zn\">2.</span> Який займає великий відрізок часу; тривалий,\nдовгочасний. <i class=\"illus\">Довгими осінніми вечорами велись\nбезконечні розмови та суперечки</i> <span class=\"s\">(Михайло Коцюбинський, II, 1955, 66)</span>;\n<i class=\"illus\"><span class=\"sq\">[Дубина:]</span> У нас з тобою буде ще довга розмова</i>\n<span class=\"s\">(Захар Мороз, П'єси, 1959, 216)</span>; <i class=\"illus\">Почався довгий і впертий штурм\nгранітної стіни</i> <span class=\"s\">(Олесь Гончар, III, 1959, 99)</span>.\n<br/><span class=\"diam\">♦</span> <span class=\"z\">Відкладати (відкласти) в довгий ящик (в\nдовгу шухляду)</span> — відкладати виконання якої-небудь\nсправи на тривалий, невизначений час. <i class=\"illus\">Центральна\nрада, не відкладаючи справу в довгу шухляду, одразу\nпродала Україну німцям</i> <span class=\"s\">(Остап Вишня, I, 1956, 445)</span>;\n<span class=\"z\">Довгий карбованець</span> — легкий і великий\nзаробіток. <i class=\"illus\"><span class=\"sq\">[Семен:]</span> Тепер хай мені хтось заїкнеться,\nщо ваша бригада за довгим карбованцем лізе...</i> <span class=\"s\">(Ігор Муратов,\nРадісний берег, 1961, 83)</span>; <i class=\"illus\">Той, хто їхав за довгим\nкарбованцем, залишив новобудову — не витримав\nтруднощів</i> <span class=\"s\">(Радянська Україна, 26.XI 1961, 2)</span>; <span class=\"z\">Довга лоза</span> — гра, яка\nполягає в тому, що один з її учасників повинен\nперестрибнути через інших, що розмістились один за одним\nзігнувшись. <i class=\"illus\"><span class=\"sq\">[Мотря:]</span> Парубки гратимуть у довгої\nлози, у тарана; дівчата — у ворона, у гусей!..</i> <span class=\"s\">(Марко Кропивницький,\nII, 1958, 25)</span>; <span class=\"z\">Довга пісня</span> — про те, що займає\nвеликий відрізок часу, чого не можна швидко зробити,\nвиконати, розповісти. <i class=\"illus\">— Ага, що це у вас тут з Ганною\nскоїлося? — дивлячись на сестру, запитав Данько.\n— Довга пісня, — жваво заговорила Вутанька</i> <span class=\"s\">(Олесь Гончар,\nII, 1959, 142)</span>; <span class=\"z\">Довгий язик</span> — про балакливу людину,\nщо говорить зайве, або про її вдачу. <i class=\"illus\">— Хай собі довгі\nязики що хочуть говорять: ротів людям не позамазуєш\nі слухати — не переслухаєш</i> <span class=\"s\">(Панас Мирний, IV, 1955, 296)</span>;\n<i class=\"illus\">Я бачив, що моя розповідь схвилювала її, і\nжорстоко картав себе за довгий язик</i> <span class=\"s\">(Микола Трублаїні, III,\n1956, 281)</span>.</p></div>"""
# test_article_ = """<div itemprop=\"articleBody\"><p><strong class=\"title\" itemprop=\"headline\">ЗАКРУЧУВАТИ</strong>, ую, уєш, <abbr class=\"mark\" title=\"недоконаний вид\">недок.</abbr>, <strong class=\"title\">ЗАКРУТИТИ</strong>,\nучу, утиш, <abbr class=\"mark\" title=\"доконаний вид\">док.</abbr> </p><p class=\"znach\"><span class=\"zn\">1.</span> <abbr class=\"mark\" title=\"перехідне дієслово\">перех.</abbr> Обертати, рухати що-небудь\nпо колу; <br/><span class=\"tinok\">//</span>  Надавати чому-небудь вихрового руху. <i class=\"illus\">Од\nшвидкого руху вода пінилась і крутилась у вирах,\nзакручуючи тріски, дошки, стовбури дерев</i> <span class=\"s\">(Микола Трублаїні, I, 1955,\n90)</span>; <i class=\"illus\">Омелько якимсь невловимим рухом спритно\nзакрутив молоко в глечику, налив у кухлі, не схлюпнувши</i>\n<span class=\"s\">(Микола Рудь, Гоміп.., 1959, 26)</span>.\n<br/><span class=\"diam\">♦</span> <span class=\"z\">Закрутити веремію</span> див. <a href=\"http://sum.in.ua/s/veremija\">веремія</a>.\n</p><p class=\"znach\"><span class=\"zn\">2.</span> <abbr class=\"mark\" title=\"перехідне дієслово\">перех.</abbr> Загвинчуючи, укріпляти в чомусь,\nзакривати що-небудь. <i class=\"illus\">Слідом ішли монтери, ..закручували білі\nчашечки ізоляторів</i> <span class=\"s\">(Василь Кучер, Трудна любов, 1960, 425)</span>;\n<i class=\"illus\">Ватя ледве встигла поставити чайник на стіл і\nзакрутити кран самовара</i> <span class=\"s\">(Нечуй-Левицький, IV, 1956, 64)</span>; <i class=\"illus\">Для себе\nГнат.. закрутив у тиски металеву планку</i> <span class=\"s\">(Степан Чорнобривець,\nВизволена земля, 1959, 56)</span>; <br/><span class=\"tinok\">//</span>  Загвинчуючи чим-небудь,\nзакриваючи закруткою тощо, замикати (двері і т. ін.).\n<i class=\"illus\">Денис зачиня, приклада замки, закручує <span class=\"sq\">[їх]</span></i> <span class=\"s\">(Квітка-Основ'яненко,\nII, 1956, 406)</span>; <i class=\"illus\">Христя кинулась до надвірних дверей,\n..зачинила й закрутила заверткою</i> <span class=\"s\">(Панас Мирний, II, 1954,\n168)</span>; <i class=\"illus\">Зоя закрила піч, закрутила дверцята</i> <span class=\"s\">(Вадим Собко, Біле\nполум'я, 1952, 249)</span>.\n<br/><span class=\"diam\">♦</span> <span class=\"z\">Закручувати (закрутити) гайку</span> див. <a href=\"http://sum.in.ua/s/ghajka\">гайка</a>.\n</p><p class=\"znach\"><span class=\"zn\">3.</span> <abbr class=\"mark\" title=\"перехідне дієслово\">перех.</abbr> Обвиваючи, зав'язувати навколо чого-небудь\nабо намотувати на щось. <i class=\"illus\">Вдягався <span class=\"sq\">[Синявін]</span> в\nузбецький одяг, навіть чалму сніжно-білу.. закручував на\nлису голову і їхав у гори</i> <span class=\"s\">(Іван Ле, Міжгір'я, 1953, 69)</span>; <i class=\"illus\">Карпо\nзломив верх високої чорнобилини і закрутив кругом\nстерна</i> <span class=\"s\">(Панас Мирний, I, 1954, 247)</span>.\n</p><p class=\"znach\"><span class=\"zn\">4.</span> <abbr class=\"mark\" title=\"перехідне дієслово\">перех.</abbr> Звивати джгутом, зав'язувати що-небудь\nу вузол і т. ін. <i class=\"illus\">Дорогою зірвав <span class=\"sq\">[дід]</span> по кущику\nгорицвіту, золототисячнику і дроку, згорнув докупи, закрутив\nі заткнув собі за лівий чобіт</i> <span class=\"s\">(Олекса Стороженко, I, 1957, 90)</span>; <i class=\"illus\">Марипя\nперестала бавитись волоссям, закрутила його недбало\nу вузол</i> <span class=\"s\">(Ірина Вільде, Сестри.., 1958, 341)</span>; <br/><span class=\"tinok\">//</span>  Завивати (вуса,\nволосся). <i class=\"illus\">Кум-полковник, ..огрядний, кругловидий,\nчервоний, усе вуса закручує правицею</i> <span class=\"s\">(Марко Вовчок, I, 1955,\n133)</span>; <br/><span class=\"tinok\">//</span>  Виводячи криву лінію, загинати її донизу,\nвбік і т. ін. <i class=\"illus\">Яків узяв перо... усі здивувались —\nвитріщились. А він.. виводе <span class=\"sq\">[виводить]</span>: Яків Карпович\nБородай, — ще й крюк закрутив</i> <span class=\"s\">(Панас Мирний, I, 1954, 203)</span>.\n</p><p class=\"znach\"><span class=\"zn\">5.</span> <abbr class=\"mark\" title=\"тільки доконаний вид\">тільки док.</abbr>, <abbr class=\"mark\" title=\"перехідне дієслово\">перех.</abbr>, <abbr class=\"mark\" title=\"переносне значення\">перен.</abbr> Захопити цілком, не ли1\nшаіочи вільного часу. <i class=\"illus\">В перші дні після випуску, як\nтільки пішла <span class=\"sq\">[Настя]</span> на ферму, зробила кілька записів,\nа потім закрутило життя, з ранку і допізна на роботі,\nніколи було за перо взятись</i> <span class=\"s\">(Іван Цюпа, Вічний вогонь,\n1960, 90)</span>.\n</p><p class=\"znach\"><span class=\"zn\">6.</span> <abbr class=\"mark\" title=\"тільки доконаний вид\">тільки док.</abbr>, <abbr class=\"mark\" title=\"перехідне дієслово\">перех.</abbr>, <abbr class=\"mark\" title=\"переносне значення\">перен.</abbr>, <abbr class=\"mark\" title=\"розмовне\">розм.</abbr> Діючи певним\nчином, викликати у когось почуття кохання; закохати.\n<i class=\"illus\"><span class=\"sq\">[Пилип:]</span> Гляди ж мені, не упусти такого жениха,\nяк Никодим.. Та тебе не треба вчить, закрутиш хоч\nкого</i> <span class=\"s\">(Карпенко-Карий, I, 1960, 425)</span>.\n</p><p class=\"znach\"><span class=\"zn\">7.</span> <abbr class=\"mark\" title=\"неперехідне дієслово\">неперех.</abbr>, <abbr class=\"mark\" title=\"переносне значення\">перен.</abbr> Говорити хитромудро,\nвигадливо або пишномовно. <i class=\"illus\"><span class=\"sq\">[Катря:]</span> Професор таке\nговорить на лекції, що в голові макітриться, нічого не\nрозумієш.. А він ще навмисне закручує. От закручує, закручує,\nщоб незрозуміліш було</i> <span class=\"s\">(Іван Микитенко, I, 1957, 131)</span>; <i class=\"illus\">— Любов рухає\nармії... хм... закрутив, — посміхнувся Сагайда,\nпригадуючи, що колись уже чув щось подібне від Брянського</i>\n<span class=\"s\">(Олесь Гончар, III, 1959, 318)</span>.\n</p><p class=\"znach\"><span class=\"zn\">8.</span> <abbr class=\"mark\" title=\"перехідне дієслово\">перех.</abbr>, <abbr class=\"mark\" title=\"переносне значення\">перен.</abbr> Заплутувати яку-небудь справу.\n<i class=\"illus\"><span class=\"sq\">[Передерій:]</span> Адже як почне <span class=\"sq\">[Стрижаченко]</span>\nкрутити, як почне вертіти, то й праве діло так закруте\n<span class=\"sq\">[закрутить]</span>, що сам чортяка.. в його правди не\nдошукається</i> <span class=\"s\">(Панас Мирний, V, 1955, 123)</span>.\n<br/><span class=\"diam\">♦</span> <span class=\"z\">Закручувати (закрутити) голову</span> див. <a href=\"http://sum.in.ua/s/gholova\">голова</a>;\n<span class=\"z\">Закручувати (закрутити) любов</span> — залицятися, вступати\nв любовні стосунки. <i class=\"illus\">Так, от же чортова баба, — сама\nдо парубка в'язне, при людях прямо. А потім разом із\nмлина і вони, і він, Гнида, пішов. Так біля воріт\nМотузчиних бачив: закручують уже любов</i> <span class=\"s\">(Андрій Головко, II,\n1957, 69)</span>; <span class=\"z\">Закрутити на вус</span> див. <a href=\"http://sum.in.ua/s/vus\">вус</a>; <span class=\"z\">Закручувати одну\nі ту ж пластинку</span> — говорити весь час те саме.\n<i class=\"illus\">Бурчить <span class=\"sq\">[теща]</span>, зітха, одну і ту ж Закручує пластинку:\n— Чого женивсь? Який ти муж? Ти любиш м'яч, не\nжінку!</i> <span class=\"s\">(Степан Олійник, Вибр., 1959, 266)</span>; <span class=\"z\">Закрутити світ</span> див. <a href=\"http://sum.in.ua/s/svit\">світ</a> 1;\n<span class=\"z\">Закрутити харамана</span> див. <a href=\"http://sum.in.ua/s/kharaman\">хараман</a>.</p></div>"""
#
# idioms = parse(test_article)
# print("RESULT: ", len(idioms))
# [print(idiom) for idiom in idioms]