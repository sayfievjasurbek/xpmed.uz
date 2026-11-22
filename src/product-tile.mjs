import { escape } from './html.mjs';
import { icon } from './icons.mjs';

export function renderTileImage(product, className) {
  const imageType = product.imageType === 'scene' ? 'scene' : 'cutout';
  const dimensions = product.imageDimensions?.[product.image];
  const cap = dimensions ? ` style="max-width:min(100%, ${Number(dimensions.width)}px);max-height:min(100%, ${Number(dimensions.height)}px);place-self:center" width="${Number(dimensions.width)}" height="${Number(dimensions.height)}"` : '';
  return `<div class="tile-image ${className}" data-image-type="${imageType}">
    <img src="${escape(product.image)}" alt=""${cap} loading="lazy" decoding="async">
  </div>`;
}

export function renderProductTile(product, lang, learnMore, searchTerms) {
  const name = product['name_' + lang];
  const tagline = product['tagline_' + lang];
  const description = product['description_' + lang];
  const productPage = product.documents.find(({ type }) => type === 'product-page');
  const filterData = searchTerms === undefined ? '' :
    ` data-name="${escape(name)}" data-new="${!!product.isNew}" data-subcategory="${escape(product.taxonomySubcategory||'')}" data-brand="${escape(product.brand)}" data-area="${escape(product.area||'')}" data-type="${escape(product.productType||'')}"
        data-specialty="${escape(product.specialty.join(' '))}" data-catalogs="${escape((product.catalogs||[]).join(' '))}" data-keywords="${escape(searchTerms)}"`;

  return `<article class="product-tile"${filterData}>
    <a href="${escape(productPage[lang])}" class="product-tile__link" aria-label="${escape(name + ' · ' + learnMore)}"${description ? ` aria-description="${escape(description)}"` : ''}>
      ${renderTileImage(product, 'product-tile__image')}
      <div class="product-tile__caption">
        <div><h3>${escape(name)}</h3><p>${escape(tagline)}</p></div>
        ${icon('circleArrow')}
      </div>
    </a>
  </article>`;
}
