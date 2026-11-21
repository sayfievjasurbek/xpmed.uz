export const clinicalSpecialties = ['orthopedics', 'traumatology', 'spine', 'sports', 'surgery', 'cardiothoracic', 'ent', 'neurosurgery', 'pediatric-orthopedics'];
const specialtyAliases = {'Детская ортопедия':'pediatric-orthopedics','Pediatric orthopedics':'pediatric-orthopedics','Cardiothoracic surgery':'cardiothoracic','Кардиоторакальная хирургия':'cardiothoracic','ENT':'ent','Оториноларингология (ЛОР)':'ent','Neurosurgery':'neurosurgery','Нейрохирургия':'neurosurgery','Orthopedics':'orthopedics','Ортопедия':'orthopedics','Traumatology':'traumatology','Травматология':'traumatology','Spine surgery':'spine','Хирургия позвоночника':'spine','Sports medicine':'sports','Спортивная медицина':'sports','General surgery':'surgery','Общая хирургия':'surgery'};
const subcategoryAliases = {'Тазобедренный сустав':'hip','Hip':'hip','Hip joint':'hip','Knee surgery':'knee','Хирургия коленного сустава':'knee','Коленный сустав':'knee','Shoulder surgery':'shoulder','Хирургия плечевого сустава':'shoulder','Плечевой сустав':'shoulder'};
export function normalizeTaxonomy(system) {
  if (!Array.isArray(system.specialty)) return system;
  const specialties = [], subcategories = [...(system.subcategories || []), ...(system.subcategory ? [system.subcategory] : [])];
  for (const value of system.specialty) {
    const key = specialtyAliases[value] || value;
    if (clinicalSpecialties.includes(key)) specialties.push(key);
    else subcategories.push(subcategoryAliases[value] || value);
  }
  const unique = [...new Set(subcategories.map(value => subcategoryAliases[value] || value).filter(Boolean))];
  return {...system, specialty: [...new Set(specialties)], subcategories: unique, subcategory: unique[0] || ''};
}
