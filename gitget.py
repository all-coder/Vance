import requests

class Vance_Github:
  @staticmethod
  def get_github_repos(username):
    url =f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    user_repos_list = []
    if(response.status_code==200):
      user_repos = response.json()
      for i in user_repos:
        temp = [i['name'],i['description'],i['html_url']]
        user_repos_list.append(temp)
    else:
      return False
    return user_repos_list
  
  @staticmethod
  def get_github_query_result(query,sort="stars",order="desc",per_page=5,page=1):
    result=[]
    url = "https://api.github.com/search/repositories"
    params = {
      "q":query,
      "sort":sort,
      "order":order,
      "per_page":per_page,
      "page":page
    }
    response = requests.get(url,params=params)
    if(response.status_code==200):
      result = response.json().get('items',[])
      return result
    else:
      return False
