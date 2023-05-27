import os
from flask import Flask, render_template, request, jsonify, redirect, session
import bcrypt
# from flask_bcrypt import Bcrypt
import json
from datetime import datetime, timedelta
import shutil
import urllib.parse

from app.models import session_scope, User, Information, Weddinghall, Transportation, Account, Guestbook, Transportationtype, Textlist, Texttype, Picture, Picturetype, UserHasTemplate
from app.config import secret_key, bcrypt_level
from app.views.index import geocoding


from app.views.template_dummy import groom_dict, bride_dict, wedding_schedule_dict, message_templates_dict, transport_list, guestbook_list, image_list, bank_acc
groom_dict = groom_dict # 신랑 데이터
bride_dict = bride_dict # 신부 데이터
wedding_schedule_dict = wedding_schedule_dict # 장소와 시간 데이터
message_templates_dict = message_templates_dict # 글귀 데이터
transport_list = transport_list # 교통 수단 데이터
guestbook_list = guestbook_list # 방명록 데이터
image_list = image_list # 이미지 데이터
bank_acc = bank_acc # 계좌번호 데이터


def create_app():
    app = Flask(__name__)
    # 앱 설정, 라우트, 확장 등을 여기에 추가
 
 
    app.config['SECRET_KEY'] = secret_key
    app.config['BCRYPT_LEVEL'] = bcrypt_level

    # bcrypt_app = Bcrypt(app) 

    @app.route('/pop_up', methods=['POST', 'GET'])
    def pop_up():
        contents = request.args.get('contents')
        url = request.args.get('url')

        return render_template('/pop_up.html', contents=contents, url=url)

    def user_template_info(usertemplate_id):
        # 더미 존
        from app.views.template_dummy import groom_dict, bride_dict, wedding_schedule_dict, message_templates_dict, guestbook_list, image_list, transport_list, guestbook_password
        groom_dict = groom_dict # 신랑 데이터
        bride_dict = bride_dict # 신부 데이터
        wedding_schedule_dict = wedding_schedule_dict # 장소와 시간 데이터
        message_templates_dict = message_templates_dict # 글귀 데이터
        transport_list = transport_list # 교통 수단 데이터
        guestbook_list = guestbook_list # 방명록 데이터
        guestbook_pw = guestbook_password
        # 더미 끝
        print(guestbook_pw)

        with session_scope() as db_session:
            # groom
            groom = db_session.query(Information)\
                            .filter(Information.usertemplate_id == usertemplate_id, Information.relation_id == 1).first()
            groom_father = db_session.query(Information)\
                                   .filter(Information.usertemplate_id == usertemplate_id, Information.relation_id == 3).first()
            groom_mother = db_session.query(Information)\
                                    .filter(Information.usertemplate_id == usertemplate_id, Information.relation_id == 5).first()
            groom_dict = {
                "firstname" : groom.first_name,
                "lastname" : groom.last_name,
                "phoneNum" : groom.tel,
                "father": groom_father.last_name + groom_father.first_name,
                "fatherFirstName" : groom_father.first_name,
                "fatherLastName" : groom_father.last_name,
                "fatherPhoneNum" : groom_father.tel,
                "mother" : groom_mother.last_name + groom_mother.first_name,
                "motherFirstName" : groom_mother.first_name,
                "motherLastName" : groom_mother.last_name,
                "motherPhoneNum" : groom_mother.tel,
                "relation" : "아들",
            }
            
            # bride
            bride = db_session.query(Information)\
                            .filter(Information.usertemplate_id == usertemplate_id, Information.relation_id == 2).first()
            bride_father = db_session.query(Information)\
                                   .filter(Information.usertemplate_id == usertemplate_id, Information.relation_id == 4).first()
            bride_mother = db_session.query(Information)\
                                    .filter(Information.usertemplate_id == usertemplate_id, Information.relation_id == 6).first()
            bride_dict = {
                "firstname" : bride.first_name,
                "lastname" : bride.last_name,
                "phoneNum" : bride.tel,
                "father": bride_father.last_name + bride_father.first_name,
                "fatherFirstName" : bride_father.first_name,
                "fatherLastName" : bride_father.last_name,
                "fatherPhoneNum" : bride_father.tel,
                "mother" : bride_mother.last_name + bride_mother.first_name,
                "motherFirstName" : bride_mother.first_name,
                "motherLastName" : bride_mother.last_name,
                "motherPhoneNum" : bride_mother.tel,
                "relation" : "딸",
            }

            # wedding
            wedding_item = db_session.query(Weddinghall)\
                                .filter(Weddinghall.usertemplate_id ==usertemplate_id).first()
            
            weekdays = ['월', '화', '수', '목', '금', '토', '일']
            date = wedding_item.date.weekday()

            wedding_schedule_dict = {
                'date' : (wedding_item.date).strftime('%Y년 %m월 %d일'),
                'date_format' : (wedding_item.date).strftime('%Y-%m-%d'),
                'time' : '{}요일 {}'.format(weekdays[date], wedding_item.time),
                'time_hour' : (wedding_item.time).split('시')[0]+'시',
                'time_minute' : (wedding_item.time).split('시')[1],
                'hall_detail' : wedding_item.name + wedding_item.address_detail ,
                'hall_name' : wedding_item.name,
                'hall_floor' : wedding_item.address_detail,
                'hall_addr' : wedding_item.address,
                'lat' : wedding_item.lat,
                'lng' : wedding_item.lng
            }


            # message
            message_templates_dict = {}
            message_type = db_session.query(Texttype).all()
            message_query = db_session.query(Textlist)\
                                    .filter(Textlist.usertemplate_id == usertemplate_id)
            for i, m in enumerate(message_type):
                message_templates_dict[m.name] = (message_query.filter(Textlist.text_type == i+1).first()).contents


            # tramsport
            transportation_type = db_session.query(Transportationtype).all()
            transporation_query = db_session.query(Transportation)\
                                    .filter(Transportation.usertemplate_id == usertemplate_id)
            
            transport_list = []

            # 현재 URL 경로 가져오기
            current_path = urllib.parse.urlparse(request.url).path
            for i ,t in enumerate(transportation_type):
                content = (transporation_query.filter(Transportation.transportation_type == i+1).first()).contents
                transport_item = {
                    "title_transport": t.name,
                    "contents_transport": content
                }
                if current_path == '/invitation' and content != '':
                    transport_list.append(transport_item)
                else:
                    transport_list.append(transport_item)



            # guestbook
            guestbook_items = db_session.query(Guestbook)\
                                    .filter(Guestbook.usertemplate_id == usertemplate_id).all()

            guestbook_list = []
            for g in guestbook_items:
                if i >= 5:
                    break
                guestbook_list.append({
                    "id" : g.id,
                    "name" : g.writer,
                    "content_guestbook" : g.contents,
                    "password" : g.writer_pw,
                    "created_at" : (g.created_at).strftime('%Y.%m.%d')
                })
            if len(guestbook_list) == 0:
                guestbook_list.append({
                    "id" : '',
                    "name" : '큐피트',
                    "content_guestbook" : '🌿신랑 신부의 결혼🌸의 축복해주세요🌼',
                    "password" : '',
                    "created_at" : ''
                })
            
            # image
            image_query = db_session.query(Picture)\
                                .filter(Picture.usertemplate_id == usertemplate_id)
            image_list = {}
            image_list['main_img'] = (image_query.filter(Picture.picture_type == 1).first()).url
            image_list['sub_img'] = (image_query.filter(Picture.picture_type == 2).first()).url
            
            gallery_img_list = []
            img_list = image_query.filter(Picture.picture_type == 3).order_by(Picture.priority).all()
            img_sm_list = image_query.filter(Picture.picture_type == 4).order_by(Picture.priority).all()
            print('sm)list',img_sm_list)
            for i in range(len(img_sm_list)):
                print("comming")
                gallery_img_list.append({
                    'img' : img_list[i].url,
                    'img_sm' : img_sm_list[i].url
                })

            image_list['gallery_img'] = gallery_img_list

            # account
            account_items = db_session.query(Account)\
                                    .filter(Account.usertemplate_id == usertemplate_id).all()
            
            groom_acc_list = []
            bride_acc_list = []
            for a in account_items:
                if a.relation_id == 1:
                    groom_acc_list.append({
                        "bank":a.acc_bank,
                        "name":a.acc_name,
                        "number":a.acc_number
                    })
                else:
                    bride_acc_list.append({
                        "bank":a.acc_bank,
                        "name":a.acc_name,
                        "number":a.acc_number
                    })

            bank_acc = [
                {
                    "group_name" : "신랑측",
                    "list" : groom_acc_list
                },
                {
                    "group_name" : "신부측",
                    "list" : bride_acc_list
                }
            ]
            
            # 방명록 관리자 비밀번호
            usertemplate_item = db_session.query(UserHasTemplate)\
                                        .filter(UserHasTemplate.id == usertemplate_id).first()
            user_item = db_session.query(User)\
                                .filter(User.id == usertemplate_item.user_id).first()
            
            guestbook_pw = {'password' : user_item.guestbook_pw}
            # image_list = image_list # 이미지 데이터   
        return groom_dict, bride_dict, wedding_schedule_dict, message_templates_dict, transport_list, guestbook_list, image_list, bank_acc, guestbook_pw

    @app.route("/")
    def index():
        if request.method == 'GET':
            print('index들어옴')
            return render_template('/index.html', 
                                   id=session['user']['id'] if 'user' in session else None) 
        
    @app.route("/invitation", methods=['POST', 'GET'])
    def invitation():
        is_sample = request.args.get('sample')

        if is_sample:       # 샘플보기
            from app.views.template_dummy import groom_dict, bride_dict, wedding_schedule_dict, message_templates_dict, transport_list, guestbook_list, image_list, bank_acc, guestbook_password
            groom_dict = groom_dict
            bride_dict = bride_dict
            wedding_schedule_dict = wedding_schedule_dict
            message_templates_dict = message_templates_dict
            transport_list = transport_list
            guestbook_list = guestbook_list
            image_list = image_list
            bank_acc = bank_acc
            guestbook_pw = guestbook_password
            # groom_dict, bride_dict, wedding_schedule_dict, message_templates_dict, transport_list, guestbook_list, image_list, bank_acc
        else:               # 내 청첩장 보기
            id = request.args.get('id', type=int)
            template_id = request.args.get('template_id', type=int)

            if id is None:      # 로그인 안 한 경우
                return render_template('pop_up.html',
                                       contents='로그인을 해주세요.',
                                       url='/login')

            with session_scope() as db_session:
                usertemplate_item = db_session.query(UserHasTemplate)\
                                            .filter(UserHasTemplate.user_id == id, UserHasTemplate.template_id == template_id).first()
                if not usertemplate_item:   # 청첩장 만들지 않은 경우
                    return render_template('pop_up.html',
                                            contents='청첩장을 만들어주세요',
                                            url='/')
                else:    
                    usertemplate_id = usertemplate_item.id
                    groom_dict, bride_dict, wedding_schedule_dict, message_templates_dict, transport_list, guestbook_list, image_list, bank_acc, guestbook_pw = user_template_info(usertemplate_item.id)
        return render_template('invitation.html',  
                            groom_dict=groom_dict, 
                            bride_dict=bride_dict,
                            wedding_schedule_dict=wedding_schedule_dict,
                            message_templates_dict=message_templates_dict,
                            transport_list=transport_list,
                            guestbook_list=guestbook_list,
                            image_list=image_list,
                            bank_acc=bank_acc,
                            usertemplate_id = usertemplate_id if not is_sample and usertemplate_item else None,
                            guestbook_pw=guestbook_pw
                            )


    @app.route("/login", methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('/login.html')
        
        if request.method == 'POST':
            data = request.get_json()
            
            id = data['id']
            pw = data['password']

            with session_scope() as db_session:
                user_item = db_session.query(User).filter(User.user_id == id).first()

                if user_item and bcrypt.checkpw(pw.encode('utf-8'), user_item.user_pw.encode('utf-8')):   # 로그인 성공
                    print("로그인성공")
                    session['user'] = {
                        'id' : user_item.id,
                        'user_id' : user_item.user_id
                    } 
                    response = jsonify({'message': 'Success'})
                    response.status_code = 200
                else:           # 로그인 실패
                    print("로그인실패")
                    response = jsonify({'message': 'Failed', 'contents':'아이디 비밀번호를 다시 확인해주세요.', 'url':'/login'})
                    response.status_code = 401
                    
            return response
        

    @app.route("/register", methods=['GET', 'POST'])
    def register():
        if request.method == 'GET':
            return render_template('/register.html')
        
        if request.method == 'POST':
            data = request.get_json()
            print(data)
            
            name = data['name']
            id = data['id']
            pwd = data['password']
            email = data['email']

            try:
                with session_scope() as db_session:
                    user_item = User(name, id, pwd, email)
                    db_session.add(user_item)
                    db_session.commit()
                    db_session.refresh(user_item)
                print("회원가입 성공")
                contents = '회원가입 성공! 로그인을 해주세요.'
                url = '/login'
                response = jsonify({'message': 'Success', 'contents':contents, 'url':url})
                response.status_code = 200
            except:
                print("회원가입 실패")
                contents = '회원가입 실패. 다시 회원가입 해주세요.'
                url = '/register'
                response = jsonify({'message': 'Failed', 'contents':contents, 'url':url})
                response.status_code = 500
            return response


    @app.route("/create", methods=['GET', 'POST'])
    def create():
        
        if request.method == 'GET':
            is_edit = request.args.get('edit')
            
            if 'user' in session:
                id = session['user']['id']
                user_id = session['user']['user_id']
                template_id = request.args.get('template_id', type=int)
            else:
                return render_template('pop_up.html',
                                       contents='로그인을 해주세요.',
                                       url='/login')
            
            with session_scope() as db_session:
                usertemplate_item = db_session.query(UserHasTemplate)\
                                            .filter(UserHasTemplate.user_id == id, UserHasTemplate.template_id == template_id).first()
                if is_edit:    # update시 기존 데이터 보냄
                    if not usertemplate_item:   # 청첩장 만들지 않은 경우
                        return render_template('pop_up.html',
                                                contents='청첩장을 만들어주세요.',
                                                url='/')
                    else:
                        groom_dict, bride_dict, wedding_schedule_dict, message_templates_dict, transport_list, guestbook_list, image_list, bank_acc, guestbook_pw = user_template_info(usertemplate_item.id)
                else:                   # create
                    if usertemplate_item:   # 이미 해당 탬플릿을 만들었다면
                        return render_template('pop_up.html',
                                                contents='이미 만든 템플릿입니다. 수정하기를 이용해주세요.',
                                                url='/')                        
                    from app.views.template_dummy_for_html import groom_dict, bride_dict, bank_acc, wedding_schedule_dict, message_templates_dict, transport_list, guestbook_list, image_list
                    # from app.views.template_dummy import groom_dict, bride_dict, bank_acc, wedding_schedule_dict, message_templates_dict, transport_list, guestbook_list, image_list
                return render_template('/create.html',  
                                    groom_dict=groom_dict, 
                                    bride_dict=bride_dict,
                                    wedding_schedule_dict=wedding_schedule_dict,
                                    message_templates_dict=message_templates_dict,
                                    transport_list=transport_list,
                                    guestbook_list=guestbook_list,
                                    image_list=image_list,
                                    bank_acc=bank_acc,
                                    template_id = template_id)
            
        if request.method == 'POST':
            try:
                id = session['user']['id']
                user_id = session['user']['user_id']

                json_data = json.loads(request.form.get('json'))
                is_edit = json_data['edit'] if 'edit' in json_data else None
                groom_dict = json_data['groom_dict']
                bride_dict = json_data['bride_dict']
                wedding_dict = json_data['wedding_schedule_dict']
                message_dict = json_data['message_templates_dict']
                guestbook_password = json_data['guestbook_password']
                bank_acc = json_data['bank_acc']
                transport_list = json_data['transport_list']
                print('bank_acc,',bank_acc)
                print("@#$groom_dict", groom_dict)
                print("@#$wedding_dict", wedding_dict)

                template_id = int(json_data['template_id'])
                with session_scope() as db_session:
                    usertemplate_item = db_session.query(UserHasTemplate)\
                                                .filter(UserHasTemplate.user_id == id, UserHasTemplate.template_id == template_id).first()
                    
                    if is_edit:    # update시 기존 데이터 다 삭제 후 다시 넣음
                        usertemplate_id = usertemplate_item.id
                        db_session.query(Account).filter(Account.usertemplate_id == usertemplate_id).delete()
                        db_session.query(Picture).filter(Picture.usertemplate_id == usertemplate_id).delete()
                        db_session.query(Textlist).filter(Textlist.usertemplate_id == usertemplate_id).delete()
                        db_session.query(Transportation).filter(Transportation.usertemplate_id == usertemplate_id).delete()
                        db_session.query(Weddinghall).filter(Weddinghall.usertemplate_id == usertemplate_id).delete()
                        db_session.query(Information).filter(Information.usertemplate_id == usertemplate_id).delete()
                        
                        # 이미지 폴더도 삭제                    
                        folder_path = 'app/static/images/users/{}/{}'.format(template_id, user_id)
                        try:
                            shutil.rmtree(folder_path)
                            print(f"{folder_path} 폴더와 하위 파일/폴더가 삭제되었습니다.")
                        except OSError as e:
                            print(f"{folder_path} 폴더 삭제에 실패했습니다: {e}")

                    else:
                        template_item = UserHasTemplate(id, template_id)
                        db_session.add(template_item)
                        db_session.commit()
                        db_session.refresh(template_item)
                    
                    usertemplate_item = db_session.query(UserHasTemplate)\
                                                .filter(UserHasTemplate.user_id == id, UserHasTemplate.template_id == template_id).first()
                    usertemplate_id = usertemplate_item.id

                    # 정보 입력 시작
                    # 신랑 / 신부 가족 정보
                    key_list = ['firstname', 'lastname', 'phoneNum', 'fatherFirstName', 'fatherLastName', 'fatherPhoneNum', 'motherFirstName', 'motherLastName', 'motherPhoneNum']
                    for i, d in enumerate([groom_dict, bride_dict]):
                        for check in range(0, 8, 3):
                            info_item = Information(d[key_list[check]], d[key_list[check+1]], d[key_list[check+2]], usertemplate_id, 1+i if check == 0 else 3+i if check == 3 else 5+i)
                            db_session.add(info_item)
                            db_session.commit()
                            db_session.refresh(info_item)

                    # 웨딩홀 정보
                    wedding_hall_item = Weddinghall(wedding_dict['hall_name'], wedding_dict['hall_addr'], wedding_dict['hall_floor'], wedding_dict['date'], wedding_dict['time_hour']+wedding_dict['time_minute'], usertemplate_id, wedding_dict['lat'], wedding_dict['lng'])
                    db_session.add(wedding_hall_item)
                    db_session.commit()
                    db_session.refresh(wedding_hall_item)

                    # 메시지
                    for i, m in enumerate(message_dict):
                        message_item = Textlist(message_dict[m], usertemplate_id, i+1)
                        db_session.add(message_item)
                        db_session.commit()
                        db_session.refresh(message_item)

                    # 방명록 비밀번호 업데이트 -> 디폴트값 0000
                    user_item = db_session.query(User).filter(User.id == id).first()
                    user_item.guestbook_pw = guestbook_password['password']
                    db_session.commit()

                    # 계좌
                    for i, group in enumerate(bank_acc):
                        for g in group['list']:
                            bank_item = Account(g['bank'], g['number'], g['name'], usertemplate_id, i+1)
                            db_session.add(bank_item)
                            db_session.commit()
                            db_session.refresh(bank_item)

                    # 대중교통
                    print("transport",transport_list)
                    print("transport",transport_list[0]['contents_transport'])
                    for i, t in enumerate(transport_list):
                        transport_item = Transportation(t['contents_transport'], usertemplate_id, i+1)
                        db_session.add(transport_item)
                        db_session.commit()
                        db_session.refresh(transport_item)


                print(request.files)
                main_img_file = request.files['main_img']
                sub_img_file = request.files['sub_img']
                # gallery_img_files = [v for k, v in request.files.items() if k.startswith('gallery_img')]
                gallery_img = {}
                gallery_img_sm = {}

                for k, v in request.files.items():
                    print("file", k, v)

                for k, v in request.files.items():
                    if k.startswith('gallery_img') and k.endswith('[img]'):
                        idx = int(k.split('[')[1].split(']')[0])
                        gallery_img[idx] = v
                    elif k.startswith('gallery_img') and k.endswith('[img_sm]'):
                        idx = int(k.split('[')[1].split(']')[0])
                        gallery_img_sm[idx] = v

                # 정렬
                gallery_imgs = [v for k, v in sorted(gallery_img.items())]
                gallery_img_sms = [v for k, v in sorted(gallery_img_sm.items())]

                # 이미지
                # ============================================================================
                # 서버에 이미지 저장 코드 완료 
                # 클레어... 저는 대충 하드코딩했는데 이거 함수 만들어서 하면 코드 깔끔해질 듯 부탁드려요~
                # 서버에 계속 파일 만들수 없으니 디비랑 연동 후 주석 제거해서 사용하기
                # 이미지 파일명은 아마 프론트에서 처리했던거 같아요~ 그냥 디비에 그대로 넣기만 하면될듯
                
                UPLOAD_FOLDER = 'app/static/images/users/'
                # upload_path = os.path.join(UPLOAD_FOLDER, user_id, str(template_id)).replace('\\', '/')
                upload_path = '{}{}/{}'.format(UPLOAD_FOLDER, user_id, template_id)
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path) # app/static/images/users/user_id/template_id 가 없으면 폴더 생성        
                main_img_file.save(os.path.join(upload_path, main_img_file.filename))
                sub_img_file.save(os.path.join(upload_path, sub_img_file.filename))
                
                print("upload_folder", UPLOAD_FOLDER)
                # upload_path = os.path.join(UPLOAD_FOLDER, user_id, str(template_id), '/gallery_img/').replace('\\', '/')
                upload_path = '{}{}/{}/{}'.format(UPLOAD_FOLDER, user_id, template_id, '/gallery_img/')
                print("\n\n\n@@@",upload_path)
                if not os.path.exists(upload_path):
                    print("comminggggggggggg")
                    os.makedirs(upload_path)
                for gallery_img in gallery_imgs:
                    gallery_img.save(os.path.join(upload_path, gallery_img.filename))
                    
                # upload_path = os.path.join(UPLOAD_FOLDER, user_id, str(template_id), '/gallery_img_sm/').replace('\\', '/')
                upload_path = '{}{}/{}/{}/'.format(UPLOAD_FOLDER, user_id, template_id, '/gallery_img_sm/')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                for gallery_img_sm in gallery_img_sms:
                    gallery_img_sm.save(os.path.join(upload_path, gallery_img_sm.filename))
                # ============================================================================
                
                # 메인
                url = '{}{}/{}/{}'.format(UPLOAD_FOLDER[3:], user_id, template_id, main_img_file.filename)
                img_item = Picture(url, usertemplate_id, 1, 1)
                db_session.add(img_item)
                db_session.commit()
                db_session.refresh(img_item)

                # 서브
                url = '{}{}/{}/{}'.format(UPLOAD_FOLDER[3:], user_id, template_id, sub_img_file.filename)
                img_item = Picture(url, usertemplate_id, 2, 1)
                db_session.add(img_item)
                db_session.commit()
                db_session.refresh(img_item)

                # 이미지들
                cnt = 1
                for i, g in enumerate(gallery_imgs):
                    url = '{}{}/{}/{}/{}'.format(UPLOAD_FOLDER[3:], user_id, template_id, 'gallery_img', g.filename)
                    img_item = Picture(url, usertemplate_id, 3, cnt)
                    db_session.add(img_item)
                    db_session.commit()
                    db_session.refresh(img_item)
                    cnt += 1

                cnt = 1
                for i, g in enumerate(gallery_img_sms):
                    url = '{}{}/{}/{}/{}'.format(UPLOAD_FOLDER[3:], user_id, template_id, 'gallery_img_sm', g.filename)
                    img_item = Picture(url, usertemplate_id, 4, cnt)
                    db_session.add(img_item)
                    db_session.commit()
                    db_session.refresh(img_item)
                    cnt += 1

                print("create_fin")
                json_data = request.form.get('json')
                if json_data:
                    data = json.loads(json_data)
                    print(data)
                response = jsonify({
                    'message': 'Success',
                    'contents': "저장 성공",
                    'url':  "/"
                })
                response.status_code = 200
            except:
                print("저장 실패")
                response = jsonify({
                    'message': 'Failed',
                    'contents': "저장 실패",
                    'url':  "/create"
                })
                response.status_code = 500
            return response



    @app.route("/search_geocoding", methods=['GET', 'POST'])
    def search_geocoding():
        if request.method == 'POST':
            data = request.get_json()
            address = data['address']
            lat_lng = geocoding(address)
            print(address, lat_lng)
            response = jsonify({
                'data' : {
                    'lat_lng' : lat_lng , 
                    'address' : address
                },
                'message': 'Success'
                })
            response.status_code = 200
            return response

    @app.route("/set_gusetbook", methods=['GET', 'POST'])
    def set_gusetbook():
        if request.method == 'POST':
            data = request.get_json()
            usertemplate_id = data['usertemplate_id']
            print(usertemplate_id)
            if usertemplate_id == 'sample':
                response = jsonify({
                    'message': 'Sample'
                })
                response.status_code = 200
                return response
            name = data['name']
            password = data['password']
            content = data['content']
            with session_scope() as db_session:
                guesstbook_item = Guestbook(name, password, content, usertemplate_id)
                db_session.add(guesstbook_item)
                db_session.commit()
                db_session.refresh(guesstbook_item)

            print(name, password, content)
            response = jsonify({
                'message': 'Success'
            })
            response.status_code = 200
            return response

    @app.route("/delete_guestbook", methods=['GET', 'POST'])
    def delete_guestbook():
        if request.method == 'POST':
            data = request.get_json()
            password = data['password']
            id = data['id']
            usertemplate_id = data['usertemplate_id']
            print('password,',password)
            print('id,',id)
            
            with session_scope() as db_session:
                if session['user']:         # 관리자가 삭제할 떄
                    usertemplate_item = db_session.query(UserHasTemplate)\
                                                .filter(UserHasTemplate.id == usertemplate_id).first()
                    user_item = db_session.query(User)\
                                        .filter(User.id == usertemplate_item.user_id).first()
                    get_pw = user_item.guestbook_pw
                    
                else:                       # 작성자가 삭제할 때
                    guestbook_item = db_session.query(Guestbook).filter(Guestbook.id == id).first()
                    get_pw = guestbook_item.writer_pw
                
                if password == get_pw:
                    db_session.query(Guestbook).filter(Guestbook.id == id).delete()
                    response = jsonify({
                        'message': 'Success'
                    })
                    response.status_code = 200
                else:
                    response = jsonify({
                        'message': 'Failed'
                    })
                    response.status_code = 401
                    
            return response
        
    @app.route('/logout')
    def logout():
        session.pop('user', None)
        return render_template('/pop_up.html', contents='로그아웃 되었습니다.', url='/login') 
        
        
        
    # @app.route("/create_account", methods=['GET', 'POST'])
    # def create_account():
    #     name = request.form.get('name')
    #     id = request.form.get('id')
    #     pwd = request.form.get('pwd')
    #     email = request.form.get('email')

    #     with session_scope() as db_session:
    #             user_item = User(name, id, pwd, email)
    #             db_session.add(user_item)
    #             db_session.commit()
    #             db_session.refresh(user_item)

    #     return render_template('/create.html')
    return app



app = create_app()


if __name__ == '__main__':
    app.run()
