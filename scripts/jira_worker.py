from jira import JIRA
import scripts.settings.jira_auth as auth
import re
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import scripts.logger as logger

maxResultsToReturn = 2000
stops = set(stopwords.words("english"))
stemmer = SnowballStemmer('english')


def connect_to_jira():
    logger.logger.info("Connecting to JIRA.")
    return JIRA(auth.jira_url, auth=(auth.jira_username,auth.jira_password))

def remove_code_from_comments(comment_body):
    return re.sub('{code:.*}([\s\S]*?){code}','',str(comment_body))

def get_jira_issue_object(authed_jira, jira_name):
    return authed_jira.issue(jira_name)

def get_title(jira_issue_object):
    return jira_issue_object.fields.summary

def get_summary(jira_issue_object):
    return jira_issue_object.fields.description

def get_jira_id(jira_issue_object):
    return jira_issue_object.key

def get_status(jira_issue_object):
    return jira_issue_object.fields.status

def get_list_of_comments(jira_issue_object):
    return jira_issue_object.fields.comment.comments

def get_reqd_comments_data(list_of_comments_object):
    ticket_dict = {}
    ticket_dict['comments_data'] = []
    ticket_dict['comments_corpus'] = []
    for comment in list_of_comments_object:
        comment_data = {}
        comment_data['emailAddress'] = comment.author.emailAddress
        comment_data['body'] = comment.body
        comment_data['created'] = comment.created
        comment_data['updated'] = comment.updated
        ticket_dict['comments_data'].append(comment_data)
        comment_corpus_data = remove_code_from_comments(comment_data['body'])
        ticket_dict['comments_corpus'].append(comment_corpus_data)
    return ticket_dict['comments_data'],ticket_dict['comments_corpus']

def filter_crawler(authed_jira, jira_filter):
    logger.logger.debug("Crawling the filter - "+jira_filter)
    filter_tickets = authed_jira.search_issues(jira_filter, maxResults=maxResultsToReturn)
    tickets_corpus = []
    for ticket in filter_tickets:
        ticket_dict = {}
        jira_id = get_jira_id(ticket)
        ticket_dict['jiraid'] = jira_id
        ticket_dict['title'] = get_title(ticket)
        ticket_dict['summary'] = get_summary(ticket)
        # Uncomment the 3 lines below to get comments data as well
        # ticket_full_data = authed_jira.issue(jira_id)
        # list_of_comments = get_list_of_comments(ticket_full_data)
        # ticket_dict['comments_data'],ticket_dict['comments_corpus'] = get_reqd_comments_data(list_of_comments)
        tickets_corpus.append(ticket_dict)
    logger.logger.debug("Crawling done. Ticket corpus - "+str(tickets_corpus))
    return tickets_corpus

def comment_on_task(authed_jira,jira_id,comment):
    logger.logger.debug("Commenting - "+str(comment)+" on ",jira_id)
    try:
        authed_jira.add_comment(jira_id,comment)

    except Exception as e:
        logger.exception(e)
        logger.sentry_client.captureException()


