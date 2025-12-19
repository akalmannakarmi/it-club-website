from django.db import models




#Resource  for A single Topic (video and description )
class Topic(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)    
    recorded_video = models.FileField(blank = True , null = True) 
    youtube_url = models.URLField(blank = True , null = True)

    """
    recorded_video is for the sessions conducted by the club.
    If the a session doesn't exist for a topic and is important,
    we will embed a quality youtube video onto our website for that said topic.
    """

    def get_video(self):
        return self.recorded_video.url if  self.recorded_video else self.youtube_url 
    """
    get_video returns a recorded video string A path if a recorded_video exists 
    If not  then a url to a yt video
    """
    
    def __str__(self):
        return self.name
    


#For Extra resources(yt links, books,pdf) of the same above Topic 
class ResourceExtra(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="extras") # references the above topic field 
    title = models.CharField(max_length=200, blank=True)
    url = models.URLField(blank=True, null=True)                                 #for youtube videos
    file = models.FileField(blank=True, null=True)  #for books,notes,pdf's
    description = models.TextField(blank=True)  

    def __str__(self):
        return self.title if self.title else "Extra Resource"
    
