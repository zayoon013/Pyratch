from datetime import datetime
import json
import scratchattach
from flask import Flask, render_template, request
app = Flask(__name__)

DEFAULT_SETTINGS = {
	"turbowarp-embed": False,
	"dark-mode": False
}

def with_offset(function):
    offset = 0
    result = []
    while True:
        returned = function(offset=offset)
        if not returned:
            break
        result += returned
        offset += 40
    return result

class SettingsManager:
	def __init__(self):
		try:
			with open("settings.json", "r") as settings_file:
				self.settings_json = json.load(settings_file)
		except FileNotFoundError:
			self.settings_json = DEFAULT_SETTINGS
			with open("settings.json", "w") as settings_file:
				json.dump(DEFAULT_SETTINGS, settings_file)
	def refresh_settings(self):
		with open("settings.json", "r") as file:
			self.settings_json = json.load(file)

settings_manager = SettingsManager()

def user_load(username):
    user = scratchattach.get_user(username)
    join_date = datetime.fromisoformat(user.join_date).strftime("%Y %B %d at %m:%S")
    all_followers = with_offset(user.followers)
    all_following = with_offset(user.following)
    comment_count = len(user.comments())
    all_projects = with_offset(user.projects)
    
    return user, {
        "join_date": join_date,
        "all_followers": all_followers,
        "all_following": all_following,
        "comment_count": comment_count,
        "all_projects": all_projects
    }

def user_load_user(given_user):
    user = given_user
    join_date = datetime.fromisoformat(user.join_date).strftime("%Y %B %d at %m:%S")
    all_followers = with_offset(user.followers)
    all_following = with_offset(user.following)
    comment_count = len(user.comments())
    all_projects = with_offset(user.projects)
    
    return user, {
        "join_date": join_date,
        "all_followers": all_followers,
        "all_following": all_following,
        "comment_count": comment_count,
        "all_projects": all_projects
    }

def project_load(id):
    project = scratchattach.get_project(str(id))
    num_comments = len(project.comments())
    return project, num_comments

def studio_load(id):
    studio = scratchattach.get_studio(str(id))

    host, host_info = user_load_user(studio.managers(limit=1)[0])
    all_projects = with_offset(studio.projects)
    for idx, project in enumerate(all_projects):
        all_projects[idx] = scratchattach.get_project(project["id"])
    all_curators = with_offset(studio.curators)
    all_managers = with_offset(studio.managers)

    return studio, {
        "host": host,
        "host_info": host_info,
        "all_projects": all_projects,
        "all_curators": all_curators,
        "all_managers": all_managers
    }

@app.route("/")
def root():
	return render_template("root.html", featured_projects=scratchattach.featured_projects(), dark_mode=settings_manager.settings_json["dark-mode"])

@app.route("/users/<username>")
def user(username):
	user, info = user_load(username)
	return render_template("user.html", user=user, info=info, len=len, dark_mode=settings_manager.settings_json["dark-mode"])

@app.route("/users/<username>/followers")
def user_followers(username):
	user, info = user_load(username)
	return render_template("user_followers.html", user=user, info=info, dark_mode=settings_manager.settings_json["dark-mode"])

@app.route("/users/<username>/following")
def user_following(username):
	user, info = user_load(username)
	return render_template("user_following.html", user=user, info=info, dark_mode=settings_manager.settings_json["dark-mode"])

@app.route("/users/<username>/projects")
def user_projects(username):
	user, info = user_load(username)
	return render_template("user_projects.html", user=user, info=info, len=len, dark_mode=settings_manager.settings_json["dark-mode"])

@app.route("/projects/<id>")
def project(id):
	project, comment_count = project_load(id)
	return render_template("project.html", project=project, comment_count=comment_count, dark_mode=settings_manager.settings_json["dark-mode"], turbowarp=settings_manager.settings_json["turbowarp-embed"])

@app.route("/studios/<id>")
def studio(id):
    studio, info = studio_load(id)
    return render_template("studio.html", studio=studio, dark_mode=settings_manager.settings_json["dark-mode"], info=info, len=len)

@app.route("/settings", methods=["POST", "GET"])
def settings():
    if request.method == "POST":
        turbowarp_embed = request.form.get('turbowarp-embed')
        dark_mode = request.form.get('dark-mode')
        settings_newjson = json.load(open("settings.json", "r"))
        settings_newjson["turbowarp-embed"] = turbowarp_embed == "on"
        settings_newjson["dark-mode"] = dark_mode == "on"
        with open("settings.json", "w") as f:
            json.dump(settings_newjson, f, indent=4)
        settings_manager.refresh_settings()
        return render_template("settings.html", success=True, dark_mode=settings_manager.settings_json["dark-mode"])
    else:
        return render_template("settings.html", success=False, dark_mode=settings_manager.settings_json["dark-mode"])

if __name__ == "__main__":
  app.run(debug=True)
