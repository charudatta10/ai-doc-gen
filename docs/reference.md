---
carousels:
- images: 
  - image: /assets/images/image-1.jpg
    url: post-name-1
  - image: /assets/images/image-2.jpg
    url: post-name-2
  - image: /assets/images/image-3.jpg
    url: post-name-3
---    
    
    <div class="carousel__track">
      <ul>
        {% for item in page.carousels[number].images %}
          <li class="carousel__slide" style="background-image: url('{{ item.image }}');">
            <a style="text-decoration:none;display:block;width:100%;height:100%;" href="{{ item.url }}"></a>
          </li>
        {% endfor %}
      </ul>
    </div>
