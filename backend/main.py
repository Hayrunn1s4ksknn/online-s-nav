from fastapi import FastAPI, Depends, HTTPException, status, Body, Path, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kullanıcı modeli
class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    disabled: Optional[bool] = None
    role: str
    grade: Optional[int] = None  # 9, 10, 11, 12

class UserInDB(User):
    hashed_password: str

# Şifreleme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Sahte kullanıcı veritabanı (ileride DB ile değiştirilecek)
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": get_password_hash("admin123"),
        "disabled": False,
        "role": "admin",
        "grade": None,
    },
    "student": {
        "username": "student",
        "full_name": "Student User",
        "email": "student@example.com",
        "hashed_password": get_password_hash("student123"),
        "disabled": False,
        "role": "student",
        "grade": 9,
    },
    "student2": {
        "username": "student2",
        "full_name": "Student İki",
        "email": "student2@example.com",
        "hashed_password": get_password_hash("student2123"),
        "disabled": False,
        "role": "student",
        "grade": 10,
    }
}

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

# JWT token oluşturma
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/")
def read_root():
    return {"message": "Online Sınav Platformu Backend'e Hoşgeldiniz!"}

class Question(BaseModel):
    text: str
    options: list[str]
    answer: int  # doğru şık indexi

# Soru havuzu: {ders: {sınıf: [sorular]}}
BIG_QUESTION_POOL = {
    "Matematik": {
        9: [
            {"text": "Aşağıdaki Venn şemasında\n● 4 ile tam bölünebilen tam sayılar A,\n● 6 ile tam bölünebilen tam sayılar B,\n● 5 ile tam bölünebilen tam sayılar C kümeleriyle gösterilmiştir.\nBuna göre, aşağıdaki sayılardan hangisi boyalı bölgenin bir elemanı değildir?", "options": ["A) 60", "B) 50", "C) 40", "D) 30", "E) 20"], "answer": 1},
            {"text": "A = {1, 2, 3, 5, 9}\nB = {2, 3, 10}\nC = {1, 2, 3, 9}\nkümeleri veriliyor.\nBuna göre, A , B , C kümesinin elemanlarının toplamı kaçtır?", "options": ["A) 28", "B) 30", "C) 40", "D) 45", "E) 50"], "answer": 1},
            {"text": "Türkiye'deki şehirlerin kümesi E olmak üzere, bu kümenin alt kümesi olan\nA = {En az beş harfli şehirler}\nB = {A ile başlayan şehirler}\nC = {En çok altı harfli şehirler}\nkümeleri veriliyor.\nBuna göre,\nI. Bursa ! A , C\nII. Ankara ! A + B + C\nIII. Çanakkale ! B , C\nifadelerinden hangileri doğrudur?", "options": ["A) Yalnız I", "B) Yalnız II", "C) I ve II", "D) I ve III", "E) I, II ve III"], "answer": 2},
            {"text": "p: 'N , Z– = R'\nq: 'Z 3 Q 3 R '\nr: 'Q– + Z = Q–'\nYukarıda verilen p, q ve r önermelerinin doğruluk değerleri sırasıyla aşağıdakilerden hangisidir?", "options": ["A) 1, 1, 0", "B) 1, 0, 1", "C) 1, 0, 0", "D) 0, 1, 0", "E) 0, 0, 1"], "answer": 1},
            {"text": "Aşağıda verilen sayılardan hangisi sayı doğrusunda 2 ile 3 arasında yer almaz?", "options": ["A) 23", "B) 22", "C) 7", "D) 6", "E) 5"], "answer": 2},
            {"text": "Âlim, tahtaya bir sayı doğrusu çizdikten sonra yukarıdaki şekildeki gibi bir kenarı 1 birim uzunluğunda ve bir kenarı sayı doğrusu üzerinde olan kareyi çiziyor. Daha sonra pergelinin sivri ucunu 0 noktasına batırarak yarıçapı karenin köşegeni kadar olan bir çember çiziyor ve çemberin sayı doğrusunu pozitif tarafta kestiği noktayı şekildeki gibi A olarak işaretliyor. Âlim'in çizimi üzerinden devam eden Zeynep ise önce yukarıdaki şekildeki gibi bir kenarı 1 birim ve diğer kenarı sayı doğrusu üzerinde 0'dan A'ya kadar olan bir dikdörtgen çiziyor. Sonra pergelinin sivri ucunu 0 noktasına batırarak yarıçapı dikdörtgenin köşegeni kadar olan bir çember çiziyor ve çemberin sayı doğrusunu pozitif tarafta kestiği noktayı şekildeki gibi B olarak işaretliyor. Buna göre, B noktasına karşılık gelen gerçek sayı aşağıdakilerden hangisidir?", "options": ["A) 2", "B) 25", "C) 3", "D) 27", "E) 2"], "answer": 2},
            {"text": "Aşağıdaki sayılardan hangisi bir rasyonel sayı değildir?", "options": ["A) 32-", "B) 0", "C) 37", "D) 2r", "E) 312"], "answer": 3},
            {"text": "A = {1, 2, 3, 4, 5, 6} kümesinden iki eleman çıkarılarak bir B kümesi oluşturuluyor. B kümesinin elemanlarının toplamı tek sayı olduğuna göre,\nI. A kümesinden çıkarılan iki elemandan bir tek diğer çift sayıdır.\nII. A kümesinden çıkarılan iki elemanın çarpımı çifttir.\nIII. A kümesinden çıkarılan iki elemanın toplamı çifttir.\nifadelerinden hangileri kesinlikle doğrudur?", "options": ["A) Yalnız I", "B) Yalnız II", "C) Yalnız III", "D) I ve III", "E) II ve III"], "answer": 0},
            {"text": "Karekökü tam sayı olan doğal sayılara tam kare sayılar denir. Rakamlarının sayı değerlerinin toplamına tam bölünebilen doğal sayılara Harshad sayıları denir. Buna göre, iki basamaklı tam kare sayılardan kaç tanesi Harshad sayısıdır?", "options": ["A) 5", "B) 4", "C) 3", "D) 2", "E) 10"], "answer": 1},
            {"text": "A, B ve C birer ardışık rakam olmak üzere,\nA,B\nB,C\nC,A\nondalıklı sayıları veriliyor. Bu ondalıklı sayıların toplamı 13,2 olduğuna göre,\nA : B : C çarpımının değeri kaçtır?", "options": ["A) 6", "B) 24", "C) 60", "D) 210", "E) 504"], "answer": 2},
            # ... 11-20 jenerik ...
            *[
                {"text": f"9. Sınıf Matematik Soru {i+6}", "options": [f"A{i+6}", f"B{i+6}", f"C{i+6}", f"D{i+6}"], "answer": (i % 4)}
                for i in range(15)
            ]
        ],
        10: [
            {"text": f"10. Sınıf Matematik Soru {i+1}", "options": [str(i+10), str(i+11), str(i+12), str(i+13)], "answer": (i % 4)} for i in range(20)
        ],
        11: [
            {"text": f"11. Sınıf Matematik Soru {i+1}", "options": [str(i+20), str(i+21), str(i+22), str(i+23)], "answer": (i % 4)} for i in range(20)
        ],
        12: [
            {"text": f"12. Sınıf Matematik Soru {i+1}", "options": [str(i+30), str(i+31), str(i+32), str(i+33)], "answer": (i % 4)} for i in range(20)
        ],
    },
    "Fizik": {
        9: [
            {
                "text": "Aşağıda K, L, M cisimlerinin kütleleri verilmiştir.\n• mK = 800 g\n• mL = 10000 mg\n• mM = 0,2 kg\nBuna göre mK, mL ve mM arasındaki ilişki nasıldır?",
                "options": ["A) mK > mL > mM", "B) mK > mM > mL", "C) mM > mK > mL", "D) mL > mK > mM", "E) mL > mM > mK"],
                "answer": 2
            },
            {
                "text": "K ve L sıvılarına ait kütle-hacim grafikleri Şekil 1'de verilmiştir.\nBuna göre, K, L sıvılarından yapılan homojen karışımın özkütlesi Şekil 2'de verilen grafiklerden hangisi gibi olamaz?",
                "options": ["A) Yalnız 1", "B) 1 ve 2", "C) Yalnız 5", "D) 4 ve 5", "E) 1 ve 5"],
                "answer": 2
            },
            {
                "text": "Aşağıda bazı fiziksel nicelikler verilmiştir.\n• Uzunluk\n• Basınç\n• Enerji\n• Sürat\n• Kuvvet\nBuna göre, verilen niceliklerden kaç tanesi hem skaler hem türetilmiş büyüklüktür?",
                "options": ["A) 1", "B) 2", "C) 3", "D) 4", "E) 5"],
                "answer": 2
            },
            {
                "text": "Kenar uzunlukları 6 cm, 4 cm, 8 cm olan dikdörtgenler prizması şekildeki gibi verilmiştir.\nBuna göre, prizma içine tabanı prizmanın yüzeylerinden birine paralel olacak şekilde konulan silindirin hacmi maksimum kaç santimetreküp olur? (π = 3 alınız.)",
                "options": ["A) 48", "B) 96", "C) 108", "D) 124", "E) 192"],
                "answer": 2
            },
            {
                "text": "Kütlesi m olan bir kabın 1/3'ü özkütlesi d olan sıvıyla doldurulduğunda kabın toplam kütlesi 3m olmaktadır. Aynı kap, tamamı 2d özkütleli sıvıyla doldurulursa kaptaki sıvı kütlesi kaç m olur?",
                "options": ["A) 4", "B) 6", "C) 9", "D) 12", "E) 13"],
                "answer": 1
            },
            # Geri kalan 15 soru jenerik kalsın
            *[
                {"text": f"9. Sınıf Fizik Soru {i+6}", "options": [f"FizikA{i+6}", f"FizikB{i+6}", f"FizikC{i+6}", f"FizikD{i+6}"], "answer": (i % 4)}
                for i in range(15)
            ]
        ],
        10: [
            {"text": f"10. Sınıf Fizik Soru {i+1}", "options": [str(i*3), str(i*3+1), str(i*3+2), str(i*3+3)], "answer": (i % 4)} for i in range(20)
        ],
        11: [
            {"text": f"11. Sınıf Fizik Soru {i+1}", "options": [str(i*4), str(i*4+1), str(i*4+2), str(i*4+3)], "answer": (i % 4)} for i in range(20)
        ],
        12: [
            {"text": f"12. Sınıf Fizik Soru {i+1}", "options": [str(i*5), str(i*5+1), str(i*5+2), str(i*5+3)], "answer": (i % 4)} for i in range(20)
        ],
    },
    "Kimya": {
        9: [
            {
                "text": "Bir insan vücudunda bulunabilecek elementler yaklaşık oran olarak yukarıdaki gibi belirtilmiştir. Buna göre, aşağıdaki sembollerden hangisi diğer elementler arasında yer alır?",
                "options": ["A) N", "B) B", "C) C", "D) O", "E) H"],
                "answer": 1
            },
            {
                "text": "Zeynep, evde bulunan bazı kimyasalların paket ve şişelerini yan yana koydu ve adları ile formüllerini eşleştirmeye başladı. Ancak yaptığı eşleştirme sırasında kimyasallara uymayan bir formül ile karşılaştı. Buna göre, aşağıdaki formüllerden hangisini kimyasallarla eşleştirmemiştir?",
                "options": ["A) NaOH", "B) NaClO", "C) HCl", "D) NH3", "E) CaCO3"],
                "answer": 1
            },
            {
                "text": "Beher içine konulan potas kostik bazı güvenlik sembolleri ile belirtilmek istenmektedir. Böylece kullanımı sırasında gerekli güvenlik önlemlerinin alınması istenmiştir. Buna göre, beher üzerinde soru işareti ile belirtilen alana, etiketlerinden hangileri yapıştırılmalıdır?",
                "options": ["A) Yalnız I", "B) Yalnız II", "C) I ve II", "D) I ve III", "E) II ve III"],
                "answer": 2
            },
            {
                "text": "Günlük yaşantımızda en çok kullanılan kimyasal maddelerden biri kolonyadır. Kolonya alkol ve sudan oluşan bir karışımdır. Buna göre, kolonya ile ilgili, I. Ambalajı üzerinde sembolü bulunmalıdır. II. Zehirli olmamakla birlikte içilmesi tehlikeli olan maddeler arasında yer alır. III. Ambalajında yanıcı madde olduğu belirtilmelidir. yargılarından hangileri doğrudur?",
                "options": ["A) Yalnız I", "B) Yalnız II", "C) I ve II", "D) II ve III", "E) I, II ve III"],
                "answer": 4
            },
            {
                "text": "Aşağıdaki maddelerden hangisi bir bileşik değildir?",
                "options": ["A) Kalay", "B) Kezzap", "C) Su", "D) Amonyak", "E) Sönmemiş kireç"],
                "answer": 0
            },
            # Geri kalan 15 soru jenerik kalsın
            *[
                {"text": f"9. Sınıf Kimya Soru {i+6}", "options": [f"KimyaA{i+6}", f"KimyaB{i+6}", f"KimyaC{i+6}", f"KimyaD{i+6}"], "answer": (i % 4)}
                for i in range(15)
            ]
        ],
        10: [
            {"text": f"10. Sınıf Kimya Soru {i+1}", "options": [str(i*6), str(i*6+1), str(i*6+2), str(i*6+3)], "answer": (i % 4)} for i in range(20)
        ],
        11: [
            {"text": f"11. Sınıf Kimya Soru {i+1}", "options": [str(i*7), str(i*7+1), str(i*7+2), str(i*7+3)], "answer": (i % 4)} for i in range(20)
        ],
        12: [
            {"text": f"12. Sınıf Kimya Soru {i+1}", "options": [str(i*8), str(i*8+1), str(i*8+2), str(i*8+3)], "answer": (i % 4)} for i in range(20)
        ],
    },
    "Biyoloji": {
        9: [
            {
                "text": "Hayvansal bir hücrede depo polisakkarit sentezlenirken meydana gelen değişim grafikte gösterilmiştir. Buna göre, aşağıda verilenlerden hangisi doğru eşleştirilmiştir?",
                "options": ["A) Glikojen Enzim Glikozit bağ", "B) Enzim Glikoz Glikozit bağ", "C) Glikojen Enzim Glikoz", "D) Glikojen Glikoz Glikozit bağ", "E) Su Enzim Glikojen"],
                "answer": 0
            },
            {
                "text": "I. Katabolik tepkimeleri gerçekleştirme\nII. ATP üretip kullanma\nIII. Hücresel solunum sonucunda atmosfere CO2 verme\nCanlıların tümünde yukarıda verilen özelliklerden hangileri ortaktır?",
                "options": ["A) Yalnız I", "B) Yalnız III", "C) I ve II", "D) I ve III", "E) II ve III"],
                "answer": 2
            },
            {
                "text": "Kirliliğe sebep olan zararlı maddelerin doğada ayrıştırılmasında bazı özel bakteriler kullanılmaktadır. Böylece çevre kirliliği yine canlılar kullanılarak ortadan kaldırılmaktadır. Bu yöntem aşağıdakilerden hangisi ile tanımlanır?",
                "options": ["A) Biyoremediasyon", "B) Homeostazi", "C) Adaptasyon", "D) Organizasyon", "E) Mutasyon"],
                "answer": 0
            },
            {
                "text": "• Kitin\n• Selüloz\n• Laktoz\nCanlılarda bulunan yukarıdaki moleküllerde, I. Hayvansal hücreler tarafından sentezlenme II. C, H, O elementlerine ek olarak N elementi bulundurma III. Disakkarit olma IV. Monosakkaritlerden büyük olma özelliklerinden hangileri ortak değildir?",
                "options": ["A) Yalnız I", "B) Yalnız IV", "C) I ve III", "D) II ve IV", "E) I, II ve III"],
                "answer": 4
            },
            {
                "text": "Bitki hücresinde gerçekleşen yukarıdaki tepkimeyle ilgili olarak aşağıdakilerden hangisi söylenemez?",
                "options": ["A) L, ATP molekülüdür.", "B) M organik bir maddedir.", "C) K fruktoz molekülüdür.", "D) Sükrozun yapısında glikozit bağı bulunur.", "E) Tepkime sırasında dehidrasyon gerçekleşir."],
                "answer": 0
            },
            # Geri kalan 15 soru jenerik kalsın
            *[
                {"text": f"9. Sınıf Biyoloji Soru {i+6}", "options": [f"BiyolojiA{i+6}", f"BiyolojiB{i+6}", f"BiyolojiC{i+6}", f"BiyolojiD{i+6}"], "answer": (i % 4)}
                for i in range(15)
            ]
        ],
        10: [
            {"text": f"10. Sınıf Biyoloji Soru {i+1}", "options": [f"A{i+10}", f"B{i+10}", f"C{i+10}", f"D{i+10}"], "answer": (i % 4)} for i in range(20)
        ],
        11: [
            {"text": f"11. Sınıf Biyoloji Soru {i+1}", "options": [f"A{i+20}", f"B{i+20}", f"C{i+20}", f"D{i+20}"], "answer": (i % 4)} for i in range(20)
        ],
        12: [
            {"text": f"12. Sınıf Biyoloji Soru {i+1}", "options": [f"A{i+30}", f"B{i+30}", f"C{i+30}", f"D{i+30}"], "answer": (i % 4)} for i in range(20)
        ],
    },
    "Türk Dili ve Edebiyatı": {
        9: [
            {"text": "I. Akılcılık\nII. Olgusallık\nIII. Şahsilik\nIV. Objektiflik\nV. Yararcılık\nNumaralanmış kavramlardan hangisi bilimle ilişkilendirilemez?", "options": ["A) I", "B) II", "C) III", "D) IV", "E) V"], "answer": 2},
            {"text": "I. Güzel sanatların bir dalı olan edebiyatın diğer bilimlerle ilişkisi bulunmaktadır. II. Ruh biliminden yararlanılmadan kaleme alınacak bir psikolojik romanın niteliğinden söz edilemez. III. Bir edebî eserde birden fazla bilimden yararlanılabilir. IV. Sanatçı, yapıtında toplumun kültürel kalıntılarına değinecekse sosyolojiden faydalanacaktır. V. Bilimler, yazınsal eseri sınırlar ve eserin kalitesini bozar.\nNumaralanmış cümlelerin hangisinde bilgi yanlışı vardır?", "options": ["A) I", "B) II", "C) III", "D) IV", "E) V"], "answer": 4},
            {"text": "Aşağıdaki cümlelerin hangisinde yazım yanlışı vardır?", "options": ["A) Kuşevi, kuşların barınmalarını ve korunmalarını sağlamak için ...", "B) İstanbul'un kalabalığına göre sağlıkevlerinin ne kadar az olduğunu anlattılar.", "C) Şimdi her sokakta bir tavukçu aşevi var.", "D) Zeki bakışlarıyla beni canevinden vurmaktan geri kalmadı.", "E) Kitabını basacak yayınevi bulamamış, onu kendi parasıyla bastırmak zorunda kalmıştır."], "answer": 1},
            {"text": "Kişi okuduğu edebî metinlerdeki karakterlerle dost olur ... Kişinin hissettiği duyguların başkasının ağzından bu denli güzel aktarıldığını okuması ona yalnız olmadığı hissiyatını verir.", "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."], "answer": 3},
            {"text": "5. Soru metni ...", "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."], "answer": 4},
            {"text": "Aşağıdaki cümlelerin hangisinde edebî metinlerle ilgili bilgi yanlışı vardır?", "options": ["A) İçeriği, ait olduğu toplumun ve yazıldığı dönemin niteliklerini yansıtmak zorundadır.", "B) Okuyanı etkilemelidir; anlatımı güzel, düşüncesi sağlam olmalıdır.", "C) Estetik bir güzellik yaratmayı amaçlamalıdır.", "D) Duygu ve düşünceler belli bir edebî türe uygun olarak dile getirilmelidir.", "E) Estetik ölçüler içinde, belli bir sanat anlayışıyla kaleme alınmalıdır."], "answer": 0},
            {"text": "I. Edebiyat, insanı bencillikten ve sığlıktan kurtarmaya yardımcı olur. II. Edebiyat, insanı yanlızlık duygusundan kurtarır. III. Edebiyat, betimlemeyi ve hitabeti kuvvetlendirir. IV. Edebiyat, yaratıcılığı ve düşgücünü geliştirir. V. Edebiyat; güzeli arama ve doğruya ulaşma kaygısı taşıyan insanın estetik zevkini geliştirir. Numaralanmış cümlelerin hangilerinde yazım yanlışı vardır?", "options": ["A) I ve II", "B) II ve III", "C) I ve III", "D) II ve IV", "E) IV ve V"], "answer": 0},
            {"text": "(I) Güzel sanatlarda kullanılan malzeme çok önemlidir. (II) Kullanılan malzemenin farklılığı insanın değişik duygularını hedef alarak etkilemesinden kaynaklanır. (III) Yani edebiyat ve müzik insanın işitme duyusuna hitap ederek onun değişik duygularını harekete geçirirken; heykel, resim gibi plastik sanatlar görme duyusuna yönelir. (IV) Tabii fonetik ve plastik sanatlara özgü malzemelerin karışımıyla oluşan sanatlar da vardır. (V) Karşılaştığımız bir kitabe aslında edebiyatla plastik sanatın birleşmesinden başka bir şey değildir. Numaralanmış cümlelerin hangisinde noktalama yanlışı vardır?", "options": ["A) I", "B) II", "C) III", "D) IV", "E) V"], "answer": 2},
            {"text": "Aşağıdaki cümlelerin hangisinde hikâye ile ilgili bilgi yanlışı vardır?", "options": ["A) Olay, kişi, zaman ve mekân unsurlarına yer verilir.", "B) Belli bir yazma planına sahiptir.", "C) İç konuşma, diyalog gibi anlatım teknikleri kullanılarak kaleme alınır.", "D) Olay ve kişiler kurmaca bir gerçekliğe sahiptir.", "E) Olay hikâyesinin edebiyatımızdaki önemli temsilcisi Sait Faik Abasıyanık, durum hikâyesinin ise Refik Halit Karay'dır."], "answer": 4},
            {"text": "Çarşı küf kokuyordu. Plakçı dükkânlarından taşan şarkılar birbirine karışıyordu. Eski İstanbul türkülerin söylendiği köşeleri aradı. Eski İstanbul kartları satan adamın küf kokulu kartlarına baktı. Gül yağları, kehribar tespihler satan adamlar neredeydi? Ya o türküler? Geçen günler arasında birbiriyle sohbet eden satıcılar… Bu parçayla ilgili olarak aşağıdakilerden hangisi söylenemez?", "options": ["A) Sanatsal metne örnektir.", "B) Çatışmaya yer verilmiştir.", "C) Zaman unsuru belirgin değildir.", "D) Diyalog tekniğine yer verilmemiştir.", "E) Kurmaca bir gerçekliğe sahiptir."], "answer": 1},
            # ... 11-20 jenerik ...
            *[
                {"text": f"9. Sınıf Edebiyat Soru {i+6}", "options": [f"ŞıkA{i+6}", f"ŞıkB{i+6}", f"ŞıkC{i+6}", f"ŞıkD{i+6}"], "answer": (i % 4)}
                for i in range(15)
            ]
        ],
        10: [
            {"text": f"10. Sınıf Edebiyat Soru {i+1}", "options": [f"ŞıkA{i+10}", f"ŞıkB{i+10}", f"ŞıkC{i+10}", f"ŞıkD{i+10}"], "answer": (i % 4)} for i in range(20)
        ],
        11: [
            {"text": f"11. Sınıf Edebiyat Soru {i+1}", "options": [f"ŞıkA{i+20}", f"ŞıkB{i+20}", f"ŞıkC{i+20}", f"ŞıkD{i+20}"], "answer": (i % 4)} for i in range(20)
        ],
        12: [
            {"text": f"12. Sınıf Edebiyat Soru {i+1}", "options": [f"ŞıkA{i+30}", f"ŞıkB{i+30}", f"ŞıkC{i+30}", f"ŞıkD{i+30}"], "answer": (i % 4)} for i in range(20)
        ],
    },
    "Tarih": {
        9: [
            {"text": "Tarihsel olaylar kendine has özelliklere sahiptir, somut bilgiler içerir, yer ve zaman bildirir, başlangıç ve bitiş süreleri bellidir. Özellikler dikkate alındığında aşağıdakilerden hangisi tarihsel olaya örnek gösterilemez?", "options": ["A) Sümerlerin yazıyı icadı", "B) 1230 Yassıçemen Savaşı", "C) Türkiye'nin modernleşmesi", "D) TBMM'nin Ankara'da açılması", "E) Deniz Kavimleri Hareketi"], "answer": 2},
            {"text": "Yazının icadı İlk Çağ'ın, Kavimler Göçü Orta Çağ'ın, İstanbul'un Fethi Yeni Çağ'ın, Fransız İhtilali ise Yakın Çağ'ın başlangıcı olarak kabul edilmektedir. Bu gelişmelerin çağların başlangıcı olarak alınmasında aşağıdaki özelliklerden hangisinin etkili olduğu söylenebilir?", "options": ["A) Yer bildirmesi", "B) Kullanılan aletlerin özelliği", "C) Evrensel nitelikte olması", "D) Benzer olaylar olması", "E) Deney ve gözlem metoduna dayanması"], "answer": 2},
            {"text": "'Hicri takvimin özelliklerini' yazılı sınavda soran Ali Öğretmen aşağıdaki yanıtlardan hangisini doğru cevap olarak kabul edemez?", "options": ["A) Bir yıl 354 gündür.", "B) Başlangıcı hicrettir.", "C) Ay yılına göre düzenlenmiştir.", "D) Miladi takvimle arasında 584 yıllık bir fark vardır.", "E) Hz. Ömer döneminde oluşturulan bir takvimdir."], "answer": 4},
            {"text": "Mudanya Ateşkes Antlaşması'nın cins, şekil ve içerik bakımından değerlendirmesini yapmak isteyen bir araştırmacının aşağıdaki bilim dallarının hangisinden yararlanması beklenir?", "options": ["A) Heraldik", "B) Diplomasi", "C) Antropoloji", "D) Epigrafi", "E) Arkeoloji"], "answer": 1},
            {"text": "Lidyalılar, ücretli askerlerin ücretini ödemek için parayı bulmuşlardır. Bu ifadeyi kullanan bir tarihçinin; I. nümizmatik, II. epigrafi, III. filoloji bilim dallarının hangilerinden yararlanarak bu ifadeyi kullandığı söylenebilir?", "options": ["A) Yalnız I", "B) Yalnız II", "C) Yalnız III", "D) I ve II", "E) II ve III"], "answer": 0},
            {"text": "Tarih araştırmalarında birincil el kullanmak güvenilirliği artırmakta ve hakikate ulaşmayı kolaylaştırmaktadır. Bu duruma göre, aşağıdakilerden hangisinin birincil el kaynak olduğu söylenemez?", "options": ["A) Bizans sikkeleri", "B) Kadeş Antlaşması", "C) Kültepe'deki Asurlulara ait kil tabletler", "D) İlber Ortaylı'nın 'En Uzun Yüzyıl' kitabı", "E) Kibele heykeli"], "answer": 3},
            {"text": "Büyük İskender Amon-Ra rahipleri tarafından tanrı-kral ilan edilmiş Batı Anadolu'da Didim Apollon Tapınağı kâhini tarafından 'Zeus'un Oğlu' olarak adlandırılmıştır. Bu bilgilere göre, aşağıdakilerden hangisine ulaşılamaz?", "options": ["A) Gücünün kaynağı tanrısallaşmıştır.", "B) Mısır'ı hâkimiyet altına almıştır.", "C) Doğu kültürlerinden etkilenmiştir.", "D) Akdeniz havzasını tamamen kontrol etmiştir.", "E) Teokratik bir monarşi yapısı oluşmuştur."], "answer": 3},
            {"text": "Kök Türk koruması altında Çin'den İtalya'ya kadar uzanan İpek Yolu üzerinde ticareti kontrol eden uygarlık aşağıdakilerden hangisidir?", "options": ["A) Lidyalılar", "B) Fenikeliler", "C) Soğdlar", "D) İyonlar", "E) Asurlar"], "answer": 2},
            {"text": "Mısır uygarlığında ölüler mumyalanmış ve firavunlar için piramit adı verilen anıt mezarlar yapılmıştır. Buna göre, I. Ahiret inancı görülmektedir. II. Anatomi bilimine katkıda bulunulmuştur. III. Dinî mimari örnekleri görülmüştür. yargılarından hangilerine ulaşılabilir?", "options": ["A) Yalnız I", "B) Yalnız II", "C) Yalnız III", "D) II ve III", "E) I, II ve III"], "answer": 4},
            {"text": "Aşağıdakilerden hangisinin tarih biliminin yararlarından biri olduğu söylenemez?", "options": ["A) Günümüz değer yargılarıyla geçmişi incelememizi kolaylaştırır.", "B) Bireylerde çok yönlü düşünme yeteneğini geliştirir.", "C) Birlik ve beraberliği güçlendirir.", "D) Toplumsal kimliğin inşasını sağlar.", "E) Araştırma ve kanıt bulma becerisini artırır."], "answer": 0},
            # ... 11-20 jenerik ...
            *[
                {"text": f"9. Sınıf Tarih Soru {i+6}", "options": [f"TarihA{i+6}", f"TarihB{i+6}", f"TarihC{i+6}", f"TarihD{i+6}"], "answer": (i % 4)}
                for i in range(9)
            ]
        ],
        10: [
            {"text": f"10. Sınıf Tarih Soru {i+1}", "options": [f"TarihA{i+10}", f"TarihB{i+10}", f"TarihC{i+10}", f"TarihD{i+10}"], "answer": (i % 4)} for i in range(20)
        ],
        11: [
            {"text": f"11. Sınıf Tarih Soru {i+1}", "options": [f"TarihA{i+20}", f"TarihB{i+20}", f"TarihC{i+20}", f"TarihD{i+20}"], "answer": (i % 4)} for i in range(20)
        ],
        12: [
            {"text": f"12. Sınıf Tarih Soru {i+1}", "options": [f"TarihA{i+30}", f"TarihB{i+30}", f"TarihC{i+30}", f"TarihD{i+30}"], "answer": (i % 4)} for i in range(20)
        ],
    },
    "Coğrafya": {
        9: [
            {"text": "Ülkelerin gelişmişlik düzeyi doğal çevrenin insan yaşamı üzerindeki etkisini belirleyen en önemli faktördür. Buna göre aşağıda verilenlerden hangisi yukarıda verilen duruma örnek olarak gösterilemez?", "options": ["A) Kasırga ve sellerden ABD'nin Güney Asya'dan daha az etkilenmesi", "B) Aynı şiddetteki depremin yıkıcı etkisinin Japonya'da Afganistan'dan daha az olması", "C) Meteorolojik kökenli afetlerden Endonezya'nın Avustralya'dan daha fazla etkilenmesi", "D) İran'ın ve İsviçre'nin dağlık olmasına rağmen İsviçre'de demir yolu ve kara yolu ağının daha fazla gelişmesi", "E) Kanada'da nüfusun daha çok ülkenin güneyinde toplanması"], "answer": 3},
            {"text": "Coğrafya bilimi, fiziki ve beşerî coğrafya olmak üzere ikiye ayrılır. Coğrafyanın doğal ortamlar ile bu ortamlarda meydana gelen olayları inceleyen bölümüne fiziki coğrafya, insan faaliyetlerini inceleyen bölümüne beşerî coğrafya denir. Buna göre aşağıda verilen durumlardan hangisi fiziki coğrafyanın inceleme alanına girmez?", "options": ["A) Türkiye'de batıdan doğuya doğru gidildikçe sıcaklık ortalamasının genel olarak azalması", "B) Batı rüzgârlarının orta kuşak karalarının batı kıyılarına bol yağış bırakması", "C) 30° enleminde oluşan dinamik yüksek basıncın bu alanda şiddetli kuraklığa neden olması", "D) Karadeniz Bölgesi'ndeki dağların kuzey yamaçlarında bulunan toprakların, aşırı yıkanmadan dolayı tuz ve kireç bakımından fakir olması", "E) Suriye'de yaşanan iç karışıklıklar nedeni ile insanların farklı bölgelere göç etmek zorunda kalması"], "answer": 4},
            {"text": "Aşağıda matematik iklim kuşaklarının sınırları verilmiştir. Buna göre yukarıda verilen matematik iklim kuşaklarının oluşum nedeni ile aşağıda verilenlerden hangisinin oluşum nedeni aynı değildir?", "options": ["A) Deniz seviyesinde yer çekiminin Dünya genelinde farklılık göstermesi", "B) Bir merkezde gölge boyunun yıl içerisinde sürekli olarak farklılık göstermesi", "C) Gece-gündüz süresinin yıl içerisinde değişmesi", "D) Mevsimlerin oluşması", "E) Muson rüzgârlarının oluşması"], "answer": 0},
            {"text": "Aşağıda verilenlerden hangisi Dünya'nın küresel şeklinin sonuçlarından biri değildir?", "options": ["A) Güneş ışınlarının yere düşme açısının Ekvatordan kutup noktalarına doğru gidildikçe daralması", "B) Kuzey Yarım Küre'de yaz mevsimi yaşanırken Güney Yarım Küre'de kış mevsiminin yaşanması", "C) Dünya'nın bir yarısı aydınlıkken diğer yarısının karanlık olması", "D) Yerden yükseldikçe görüş alanının genişlemesi", "E) Dünya üzerindeki bir noktadan hep aynı yönde hareket edildiğinde başlanılan noktaya geri dönülmesi"], "answer": 3},
            {"text": "Aşağıdaki Dünya haritasında aynı boylam üzerinde bulunan bazı merkezler verilmiştir. Buna göre aşağıda verilen bilgilerden hangisi bu merkezlerde yıl boyunca yaşanan ortak özelliklerden biri değildir?", "options": ["A) 23 Eylül tarihlerinde Güneş'in doğuş ve batış anları", "B) Öğle vakitleri", "C) Yerel saatleri", "D) Gün içerisinde gölge boyunun en kısa olduğu anları", "E) Çizgisel hızları"], "answer": 4},
            {"text": "Aşağıda verilenlerden hangisi, Dünya'nın günlük hareketinin sonuçlarından biri değildir?", "options": ["A) Gece ve gündüzün oluşması", "B) Güneş ışınlarının geliş açısının yıl içinde değişmesi", "C) Yerel saat farklarının oluşması", "D) Günlük sıcaklık farklarının oluşması", "E) Dinamik basınç kuşaklarının oluşması"], "answer": 1},
            {"text": "Aşağıdakilerden hangisi, Dünya'nın yıllık hareketinin sonuçlarından biri değildir?", "options": ["A) Mevsimlerin oluşması", "B) Güneş ışınlarının geliş açısının yıl içinde değişmesi", "C) Gece ve gündüz sürelerinin yıl içinde değişmesi", "D) Ekinoks ve solstislerin oluşması", "E) Yerel saat farklarının oluşması"], "answer": 4},
            {"text": "Aşağıdakilerden hangisi, harita çiziminde kullanılan projeksiyon türlerinden biri değildir?", "options": ["A) Silindirik", "B) Konik", "C) Düzlem", "D) Küresel", "E) Azimutal"], "answer": 3},
            {"text": "Aşağıdakilerden hangisi, izohips (eş yükselti) eğrileriyle ilgili yanlış bir bilgidir?", "options": ["A) Aynı eğri üzerindeki tüm noktaların deniz seviyesine olan uzaklığı aynıdır.", "B) Eğriler arasındaki mesafe azaldıkça eğim artar.", "C) Kapalı eğriler tepeyi veya çukuru gösterir.", "D) Eğriler hiçbir zaman birbirini kesmez.", "E) Eğriler arasındaki mesafe arttıkça eğim artar."], "answer": 4},
            {"text": "Aşağıdakilerden hangisi, haritalarda kullanılan ölçek türlerinden biri değildir?", "options": ["A) Kesir ölçek", "B) Çizgi ölçek", "C) Sözlü ölçek", "D) Alan ölçeği", "E) Oranlı ölçek"], "answer": 3},
            # ... 11-20 jenerik ...
            *[
                {"text": f"9. Sınıf Coğrafya Soru {i+6}", "options": [f"CoğrafyaA{i+6}", f"CoğrafyaB{i+6}", f"CoğrafyaC{i+6}", f"CoğrafyaD{i+6}"], "answer": (i % 4)}
                for i in range(5)
            ]
        ],
    },
    "Felsefe": {
        9: [
            {"text": "Felsefe ile ilgili 1. gerçek soru", "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."], "answer": 0},
            {"text": "Felsefe ile ilgili 2. gerçek soru", "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."], "answer": 1},
            {"text": "Felsefe ile ilgili 3. gerçek soru", "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."], "answer": 2},
            {"text": "Felsefe ile ilgili 4. gerçek soru", "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."], "answer": 3},
            {"text": "Felsefe ile ilgili 5. gerçek soru", "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."], "answer": 4},
            {"text": "Felsefe ile ilgili 6. gerçek soru", "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."], "answer": 0},
            {"text": "Felsefe ile ilgili 7. gerçek soru", "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."], "answer": 1},
            {"text": "Felsefe ile ilgili 8. gerçek soru", "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."], "answer": 2},
            {"text": "Felsefe ile ilgili 9. gerçek soru", "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."], "answer": 3},
            {"text": "Felsefe ile ilgili 10. gerçek soru", "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."], "answer": 4},
            *[
                {"text": f"9. Sınıf Felsefe Soru {i+11}", "options": [f"FelsefeA{i+11}", f"FelsefeB{i+11}", f"FelsefeC{i+11}", f"FelsefeD{i+11}"], "answer": (i % 4)}
                for i in range(10)
            ]
        ],
        10: [
            {"text": f"10. Sınıf Felsefe Soru {i+1}", "options": [f"FelsefeA{i+10}", f"FelsefeB{i+10}", f"FelsefeC{i+10}", f"FelsefeD{i+10}"], "answer": (i % 4)} for i in range(20)
        ],
        11: [
            {"text": f"11. Sınıf Felsefe Soru {i+1}", "options": [f"FelsefeA{i+20}", f"FelsefeB{i+20}", f"FelsefeC{i+20}", f"FelsefeD{i+20}"], "answer": (i % 4)} for i in range(20)
        ],
        12: [
            {"text": f"12. Sınıf Felsefe Soru {i+1}", "options": [f"FelsefeA{i+30}", f"FelsefeB{i+30}", f"FelsefeC{i+30}", f"FelsefeD{i+30}"], "answer": (i % 4)} for i in range(20)
        ],
    },
    "Din Kültürü": {
        9: [
            {"text": "İmanı tanımlarken 'Kalp ile tasdik etmek' ifadesi kullanılır. Tasdik, bir şeyin gerçeğe uygun olduğunu kesin bir şekilde doğrulamak, onaylamak demektir. Mümin olmanın ilk ifadesi olan kelime-i şahadeti söylerken kişi bildiğine 'tanıklık, şahitlik' eder. Bu paragrafta verilen bilgilerden yola çıkarak iman hakkında aşağıdaki sonuçlardan hangisine ulaşılabilir?", "options": ["A) Amelin imandan bir parça olmadığı", "B) İmanın amellerle olgunlaştığı", "C) İmanın temelinde tasdiğin olduğu", "D) İmanın insanı özgürleştirdiği", "E) İmanın yalnız bilgiden oluşmadığı"], "answer": 2},
            {"text": "'Hakkında kesin bilgi sahibi olmadığın şeyin peşine düşme. Çünkü kulak, göz ve kalp bunların hepsi ondan sorumludur.' (İsra suresi, 36. ayet) Aşağıdakilerden hangisi bu ayetten çıkarılacak bir sonuç değildir?", "options": ["A) İnsan duyu organlarıyla doğru bilgiye ulaşabilir.", "B) İnsanın bilgi edinme yollarından biri de akıldır.", "C) İnsan bilgi kaynaklarını doğru kullanmalıdır.", "D) Yüce Allah'a karşı nankörlük yapılmamalıdır.", "E) Bir haber hakkında hüküm vermeden önce araştırma yapılmalıdır."], "answer": 3},
            {"text": "I. Din, bağlanma, ilgi ve yansıtmadır. II. Din, manevi tecrübenin bir ürünüdür. III. Din, toplumsal hayatı düzenleme ihtiyacından kaynaklanmaktadır. Yukarıda dinin tanımı hakkında verilen yaklaşımların sebebinin aşağıdakilerden hangisi olduğu söylenemez?", "options": ["A) Materyalist ve pozitivist bakış açısı", "B) Vahiy kaynaklı bakış açısı", "C) Felsefenin bakış açısı", "D) Sosyoloji biliminin bakış açısı", "E) Psikolojinin bakış açısı"], "answer": 1},
            {"text": "İnsan, hayatı boyunca maddi ve manevi birçok şeye ilgi duyar. İnsana düşen ilgisini çeken bu şeyleri araştırmak olmalıdır. İmanın akli ve dinî delillerle kuvvetlendirilmesi gerekir. İslam inancında delillere, bilgiye, araştırmaya dayalı imana tahkiki iman denir. Delillere ve araştırmaya dayanmayan, birilerinden gördüğü şekliyle benimsenen imana ise taklidî iman denir. Taklidî iman delillere dayanmadığı için zayıftır. Taklidî imana sahip olan kişinin küçük bir engel veya itirazla karşılaştığında şüpheye düşerek imanı sarsılabilir. Buna göre aşağıdaki ayetlerden hangisi tahkiki imana yönlendirmektedir?", "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."], "answer": 4},
            {"text": "Amel ile iman arasında yakın bir ilişki vardır ancak amel, imanın bir parçası değildir. İmanın esası kalbin tasdikinden ibarettir. İmanın şartlarını kalben kabul eden bir mümin dinî vazifelerini yerine getiremese bile dinden çıkmış sayılmaz. İbadetlerini bilerek ve isteyerek yerine getirmeyen kimse günahkâr olur. İslam inancına göre eğer amel imandan bir parça sayılsaydı aşağıdaki sonuçlardan hangisine ulaşılması gerekirdi?", "options": ["A) Her günah işleyen kâfir kabul edilirdi.", "B) Büyük günah işleyenin tövbe etmesi gerekirdi.", "C) Kanaatler değişince davranışların değişmesi gerekirdi.", "D) Günahından tövbe edenlerin tövbelerinin kabul edilmesi gerekirdi.", "E) Allah'a iman etmese de salih amel işleyenlerin cennete gideceğine hükmedilirdi."], "answer": 0},
            {"text": "Aşağıdakilerden hangisi, imanın şartlarından biri değildir?", "options": ["A) Allah'a inanmak", "B) Meleklere inanmak", "C) Kitaplara inanmak", "D) Peygamberlere inanmak", "E) Namaz kılmak"], "answer": 4},
            {"text": "Aşağıdakilerden hangisi, İslam'ın şartlarından biri değildir?", "options": ["A) Kelime-i şehadet getirmek", "B) Namaz kılmak", "C) Oruç tutmak", "D) Zekat vermek", "E) Meleklere inanmak"], "answer": 4},
            {"text": "Aşağıdakilerden hangisi, Hz. Muhammed'in hayatıyla ilgili yanlış bir bilgidir?", "options": ["A) Mekke'de doğmuştur.", "B) Hira Mağarası'nda ilk vahyi almıştır.", "C) Medine'de vefat etmiştir.", "D) 40 yaşında peygamber olmuştur.", "E) 25 yaşında evlenmiştir."], "answer": 2},
            {"text": "Aşağıdakilerden hangisi, Kur'an-ı Kerim'in özelliklerinden biri değildir?", "options": ["A) Allah tarafından gönderilmiştir.", "B) Son ilahi kitaptır.", "C) 114 sureden oluşur.", "D) Sadece Araplara gönderilmiştir.", "E) Evrensel bir kitaptır."], "answer": 3},
            {"text": "Aşağıdakilerden hangisi, İslam ahlakının temel ilkelerinden biri değildir?", "options": ["A) Doğruluk", "B) Adalet", "C) Sabır", "D) Bencillik", "E) Hoşgörü"], "answer": 3},
            # ... 11-20 jenerik ...
            *[
                {"text": f"9. Sınıf Din Kültürü Soru {i+6}", "options": [f"DinA{i+6}", f"DinB{i+6}", f"DinC{i+6}", f"DinD{i+6}"], "answer": (i % 4)}
                for i in range(5)
            ]
        ],
        10: [
            {"text": f"10. Sınıf Din Kültürü Soru {i+1}", "options": [f"DinA{i+10}", f"DinB{i+10}", f"DinC{i+10}", f"DinD{i+10}"], "answer": (i % 4)} for i in range(20)
        ],
        11: [
            {"text": f"11. Sınıf Din Kültürü Soru {i+1}", "options": [f"DinA{i+20}", f"DinB{i+20}", f"DinC{i+20}", f"DinD{i+20}"], "answer": (i % 4)} for i in range(20)
        ],
        12: [
            {"text": f"12. Sınıf Din Kültürü Soru {i+1}", "options": [f"DinA{i+30}", f"DinB{i+30}", f"DinC{i+30}", f"DinD{i+30}"], "answer": (i % 4)} for i in range(20)
        ],
    },
    "İngilizce": {
        9: [
            {"text": f"9. Sınıf İngilizce Soru {i+1}", "options": [f"EnA{i}", f"EnB{i}", f"EnC{i}", f"EnD{i}"], "answer": (i % 4)} for i in range(20)
        ],
        10: [
            {"text": f"10. Sınıf İngilizce Soru {i+1}", "options": [f"EnA{i+10}", f"EnB{i+10}", f"EnC{i+10}", f"EnD{i+10}"], "answer": (i % 4)} for i in range(20)
        ],
        11: [
            {"text": f"11. Sınıf İngilizce Soru {i+1}", "options": [f"EnA{i+20}", f"EnB{i+20}", f"EnC{i+20}", f"EnD{i+20}"], "answer": (i % 4)} for i in range(20)
        ],
        12: [
            {"text": f"12. Sınıf İngilizce Soru {i+1}", "options": [f"EnA{i+30}", f"EnB{i+30}", f"EnC{i+30}", f"EnD{i+30}"], "answer": (i % 4)} for i in range(20)
        ],
    },
    "Almanca": {
        9: [
            {"text": f"9. Sınıf Almanca Soru {i+1}", "options": [f"DeA{i}", f"DeB{i}", f"DeC{i}", f"DeD{i}"], "answer": (i % 4)} for i in range(20)
        ],
        10: [
            {"text": f"10. Sınıf Almanca Soru {i+1}", "options": [f"DeA{i+10}", f"DeB{i+10}", f"DeC{i+10}", f"DeD{i+10}"], "answer": (i % 4)} for i in range(20)
        ],
        11: [
            {"text": f"11. Sınıf Almanca Soru {i+1}", "options": [f"DeA{i+20}", f"DeB{i+20}", f"DeC{i+20}", f"DeD{i+20}"], "answer": (i % 4)} for i in range(20)
        ],
        12: [
            {"text": f"12. Sınıf Almanca Soru {i+1}", "options": [f"DeA{i+30}", f"DeB{i+30}", f"DeC{i+30}", f"DeD{i+30}"], "answer": (i % 4)} for i in range(20)
        ],
    },
    "Fransızca": {
        9: [
            {"text": f"9. Sınıf Fransızca Soru {i+1}", "options": [f"FrA{i}", f"FrB{i}", f"FrC{i}", f"FrD{i}"], "answer": (i % 4)} for i in range(20)
        ],
        10: [
            {"text": f"10. Sınıf Fransızca Soru {i+1}", "options": [f"FrA{i+10}", f"FrB{i+10}", f"FrC{i+10}", f"FrD{i+10}"], "answer": (i % 4)} for i in range(20)
        ],
        11: [
            {"text": f"11. Sınıf Fransızca Soru {i+1}", "options": [f"FrA{i+20}", f"FrB{i+20}", f"FrC{i+20}", f"FrD{i+20}"], "answer": (i % 4)} for i in range(20)
        ],
        12: [
            {"text": f"12. Sınıf Fransızca Soru {i+1}", "options": [f"FrA{i+30}", f"FrB{i+30}", f"FrC{i+30}", f"FrD{i+30}"], "answer": (i % 4)} for i in range(20)
        ],
    },
}

class Exam(BaseModel):
    id: int
    title: str
    description: str
    course_id: int
    grade: int
    questions: list[Question]

class Result(BaseModel):
    username: str
    exam_id: int
    score: int
    answers: Optional[list[int]] = None

fake_exams = [
    Exam(
        id=1,
        title="9. Sınıf Matematik Deneme",
        description="9. sınıf matematik deneme sınavı",
        course_id=1,
        grade=9,
        questions=[Question(**q) for q in BIG_QUESTION_POOL["Matematik"][9]],
    ),
    Exam(
        id=2,
        title="10. Sınıf Fizik Deneme",
        description="10. sınıf fizik deneme sınavı",
        course_id=2,
        grade=10,
        questions=[Question(**q) for q in BIG_QUESTION_POOL["Fizik"][10]],
    ),
    Exam(
        id=3,
        title="11. Sınıf Kimya Deneme",
        description="11. sınıf kimya deneme sınavı",
        course_id=3,
        grade=11,
        questions=[Question(**q) for q in BIG_QUESTION_POOL["Kimya"][11]],
    ),
]

fake_results = [
    Result(username="student", exam_id=1, score=85, answers=[1,1]),
    Result(username="student", exam_id=2, score=90, answers=[0]),
    Result(username="student2", exam_id=3, score=75, answers=[0]),
]

@app.get("/exams", response_model=List[Exam])
def get_exams(course_id: int = None, grade: int = None):
    exams = fake_exams
    if course_id is not None:
        exams = [e for e in exams if e.course_id == course_id]
    if grade is not None:
        exams = [e for e in exams if e.grade == grade]
    return exams

@app.get("/results", response_model=List[Result])
def get_results(current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        return fake_results
    return [r for r in fake_results if r.username == current_user.username]

@app.post("/exams", response_model=Exam)
def add_exam(exam: Exam, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Sadece admin sınav ekleyebilir.")
    fake_exams.append(exam)
    return exam

@app.post("/take_exam", response_model=Result)
def take_exam(exam_id: int = Body(...), answers: list[int] = Body(...), current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Sadece öğrenciler sınava girebilir.")
    exam = next((e for e in fake_exams if e.id == exam_id), None)
    if not exam:
        raise HTTPException(status_code=404, detail="Sınav bulunamadı.")
    correct = sum(1 for i, q in enumerate(exam.questions) if i < len(answers) and answers[i] == q.answer)
    score = int(100 * correct / len(exam.questions))
    result = Result(username=current_user.username, exam_id=exam_id, score=score, answers=answers)
    fake_results.append(result)
    return result

# Kurs modeli
class Course(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

# Sahte kurs veritabanı
fake_courses = [
    Course(id=1, name="Matematik", description="Matematik bölümü dersleri"),
    Course(id=2, name="Fizik", description="Fizik bölümü dersleri"),
    Course(id=3, name="Kimya", description="Kimya bölümü dersleri"),
]

@app.get("/courses", response_model=List[Course])
def get_courses():
    return fake_courses

@app.post("/courses", response_model=Course)
def add_course(course: Course, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Yetkisiz işlem")
    if any(c.id == course.id for c in fake_courses):
        raise HTTPException(status_code=400, detail="Bu ID ile kurs zaten var")
    fake_courses.append(course)
    return course

@app.put("/courses/{course_id}", response_model=Course)
def update_course(course_id: int = Path(...), course: Course = Body(...), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Yetkisiz işlem")
    for idx, c in enumerate(fake_courses):
        if c.id == course_id:
            fake_courses[idx] = course
            return course
    raise HTTPException(status_code=404, detail="Kurs bulunamadı")

@app.delete("/courses/{course_id}")
def delete_course(course_id: int = Path(...), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Yetkisiz işlem")
    for idx, c in enumerate(fake_courses):
        if c.id == course_id:
            del fake_courses[idx]
            return {"detail": "Kurs silindi"}
    raise HTTPException(status_code=404, detail="Kurs bulunamadı")

class StudentCreate(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: str
    grade: int

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    disabled: Optional[bool] = None
    grade: Optional[int] = None

@app.get("/students", response_model=List[User])
def get_students(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Yetkisiz işlem")
    return [User(**u) for u in fake_users_db.values() if u["role"] == "student"]

@app.post("/students", response_model=User)
def add_student(student: StudentCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Yetkisiz işlem")
    if student.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten var")
    fake_users_db[student.username] = {
        "username": student.username,
        "full_name": student.full_name,
        "email": student.email,
        "hashed_password": get_password_hash(student.password),
        "disabled": False,
        "role": "student",
        "grade": student.grade,
    }
    return User(**fake_users_db[student.username])

@app.put("/students/{username}", response_model=User)
def update_student(username: str, student: StudentUpdate, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Yetkisiz işlem")
    if username not in fake_users_db or fake_users_db[username]["role"] != "student":
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    if student.full_name is not None:
        fake_users_db[username]["full_name"] = student.full_name
    if student.email is not None:
        fake_users_db[username]["email"] = student.email
    if student.password is not None:
        fake_users_db[username]["hashed_password"] = get_password_hash(student.password)
    if student.disabled is not None:
        fake_users_db[username]["disabled"] = student.disabled
    if student.grade is not None:
        fake_users_db[username]["grade"] = student.grade
    return User(**fake_users_db[username])

@app.delete("/students/{username}")
def delete_student(username: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Yetkisiz işlem")
    if username not in fake_users_db or fake_users_db[username]["role"] != "student":
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    del fake_users_db[username]
    return {"detail": "Öğrenci silindi"}

class RegisterRequest(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: str
    grade: int

@app.post("/register")
def register_student(data: RegisterRequest = Body(...)):
    if data.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Kullanıcı adı zaten kayıtlı.")
    hashed_pw = get_password_hash(data.password)
    fake_users_db[data.username] = {
        "username": data.username,
        "full_name": data.full_name,
        "email": data.email,
        "hashed_password": hashed_pw,
        "role": "student",
        "disabled": False,
        "grade": data.grade,
    }
    return {k: v for k, v in fake_users_db[data.username].items() if k != "hashed_password"} 