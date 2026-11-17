const legacy = 'https://xpmed.uz';
const category = '/product-category/';
const textFragment = (text) => '#:~:text=' + encodeURIComponent(text);

const paths = {
  catalog: ['/katalog/', '/catalog/'],
  double: [category + 'double-medical/', category + 'double-medical-en/'],
  conmed: [category + 'conmed/', category + 'conmed-en/'],
  synimed: [category + 'synimed/', category + 'synimed-en/'],
  trauma: [category + 'double-medical/trauma/', category + 'double-medical-en/trauma-en/'],
  hip: [
    category + 'double-medical/stenocostal-plate-ru/sistema-dlya-tazobedrennogo-sustava-joint/',
    category + 'double-medical-en/stenocostal-plate/hip-joint-system/',
  ],
  spineSystems: [
    category + 'double-medical/stenocostal-plate-ru/spinalnaya-sistema/',
    category + 'double-medical-en/stenocostal-plate/spine-system/',
  ],
  conmedImplants: [category + 'conmed/implant/', category + 'conmed-en/implant-en/'],
  knee: [category + 'conmed/kolennyj-sustav/', category + 'conmed-en/knee-joint/'],
  shoulder: [category + 'conmed/plechevoj-sustav/', category + 'conmed-en/shoulder-joint/'],
  cement: [category + 'synimed/czement-2/', category + 'synimed-en/cement/'],
  needles: [
    category + 'synimed/igla/',
    '/product/synimed-en/cement/vertebroplastiya-uchun-sinicem-steril-punching-kanulasi/',
  ],
  company: ['/o-nas/', '/about-us/'],
  certificates: ['/' + textFragment('Сертификаты'), '/homepage/' + textFragment('Certificates')],
  clients: ['/' + textFragment('Наши клиенты'), '/homepage/' + textFragment('Our clients')],
  partners: [
    '/' + textFragment('Компании, продукты которых мы поставляем'),
    '/homepage/' + textFragment('Companies whose products we supply'),
  ],
  contacts: ['/kontakty/', '/contacts/'],
};

const specialtyDestinations = {
  orthopedics: 'double',
  traumatology: 'trauma',
  spine: 'spineSystems',
  sports: 'conmed',
  surgery: 'conmed',
};

export function destination(key, lang) {
  return legacy + paths[specialtyDestinations[key] ?? key][lang === 'en' ? 1 : 0];
}

export const brands = {
  double: ['trauma', 'hip', 'spineSystems'],
  conmed: ['conmedImplants', 'knee', 'shoulder'],
  synimed: ['cement', 'needles'],
};

export const specialties = Object.keys(specialtyDestinations);
export const about = ['company', 'certificates', 'clients', 'partners'];

export const contact = {
  phone: '+998 55 500 8282',
  tel: '+998555008282',
  email: 'xpmedcompany@mail.ru',
};

export const socialLinks = {
  telegram: 'https://t.me/xpme',
  instagram: 'https://www.instagram.com/xpmed.uz/',
  facebook: 'https://www.facebook.com/xpmed.uz/',
  youtube: 'https://www.youtube.com/watch?v=E3vn7Gq2PFI',
};
