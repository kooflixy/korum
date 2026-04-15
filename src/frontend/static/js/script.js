var post_page = 0

function formate_date(date) {
    let dateObj = new Date(date)

    let formatted_date = dateObj.toLocaleString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })

    return formatted_date
}



async function get_posts_page(page) {
    let response = await (await fetch(`/api/posts/page?page=${page}`)).json()

    return response
}

function generate_post_preview(post_data) {
    let posts_list_div = document.querySelector('.posts-list')
    let post_div = document.createElement('div')

    let title = document.createElement('h3')
    title.textContent = post_data.title

    let content = document.createElement('p')
    let post_content = post_data.content
    if (post_content && post_content.length>100) {
        post_content = post_content.slice(0,100)+'...'
    }
    content.textContent = post_content

    let created_at = document.createElement('p')
    created_at.textContent = formate_date(post_data.created_at)

    post_div.append(title, content, created_at)
    posts_list_div.append(post_div)
}

async function load_posts_previews() {
    post_page = post_page + 1

    var response = await get_posts_page(post_page)

    var posts_list = response.data

    for (let post of posts_list) {
        generate_post_preview(post)
    }
    
    if (response.is_last_page == true) {
        document.querySelector('.load-posts-btn').remove()
    }

}