import json
from datetime import datetime

from operator import itemgetter
from collections import Counter
import urllib
from urllib.request import urlopen
import csv
import math
from datetime import datetime

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse


from braces.views import LoginRequiredMixin
from haystack.generic_views import SearchView

from oaiharvests.models import Community, Collection, Record, MetadataElement
from .models import StoryPage, Subscriber, ImpactFactor
from .mixins import RecordSearchMixin
from .forms import CreateSubscriberForm, UpdateImpactFactorForm, PageUpdateForm


class BaseSideMenuMixin(object):
    def get_context_data(self, **kwargs):
        context = super(BaseSideMenuMixin, self).get_context_data(**kwargs)
        try:
            context['publisher_info'] = StoryPage.objects.get(slug='publisher-info')
            context['call_l2_reading'] = StoryPage.objects.get(slug='call-l2-reading')
            context['call_reviews'] = StoryPage.objects.get(slug='call-reviews')
            context['call_open'] = StoryPage.objects.get(slug='call-open')
            context['announcements'] = StoryPage.objects.get(slug='announcements')
        except:
            context['publisher_info'] = 'Custom content expected here.'
            context['call_l2_reading'] = 'Custom content expected here.'
            context['call_reviews'] = 'Custom content expected here.'
            context['call_open'] = 'Custom content expected here.'
            context['announcements'] = 'Custom content expected here.'

        return context

class HomeView(BaseSideMenuMixin, TemplateView):
    template_name = 'home.html'
    queryset = None

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        journal = Community.objects.all()[0]
        context['keywords'] =  journal.aggregate_keywords()
        context['volumes'] = journal.list_collections_by_volume()
        # Special Issue case
        issues = journal.collection_set.all().order_by('-name')
        if issues[0].special_issue:
            try:
                context['special_issue'] = issues[0]
                context['special_issue_editors'] = context['special_issue'].edited_by.split(',')
                context['special_issue_year'] = context['special_issue'].get_collection_date()
            except:
                pass
            context['latest'] = issues[1]
        else:
            context['latest'] = issues[0]
    
        try:
            context['current_year'] = context['latest'].get_collection_date()
        except:
            context['current_year'] = datetime.now().year

        # context['latest'] = Collection.objects.all().order_by('-name')[0]
        
        context['title'] = context['latest'].title_tuple()
        context['col_break'] = context['latest'].count_records()/2
        context['toc'] = context['latest'].list_toc_by_page()

        try:
            articles = context['toc']['Article'].items()
            article_data = next(iter(articles))[1]
            # context['latest_article'] = article_data['records'][0] # ENABLE AFTER FIRST ARTICLE POSTED IN 2024
        except:
            context['empty_set'] = 'There are no records currently available for this issue.'

        try:
            context['impact_factor'] = ImpactFactor.objects.get()
        except:
            context['impact_factor'] = 0.00
        return context


class PreviousIssuesView(BaseSideMenuMixin, TemplateView):
    template_name = 'previous_issues.html'

    def get_context_data(self, **kwargs):
        context = super(PreviousIssuesView, self).get_context_data(**kwargs)
        journal = Community.objects.all()[0]
        context['volumes'] = journal.list_collections_by_volume()
        context['latest'] = [(vol, vol.list_records()) for vol in Collection.objects.all().order_by('-name')][0]
        context['curr_page'] = 'previous_issues'
        return context


class CommunityView(DetailView):
    model = Community
    template_name = 'community_view.html'

    def get_context_data(self, **kwargs):
        context = super(CommunityView, self).get_context_data(**kwargs)
        context['collections'] = self.get_object().list_collections()
        return context


class CollectionListView(ListView):
    model = Collection
    template_name = 'collection_list.html'

    def get_context_data(self, **kwargs):
        context = super(CollectionListView, self).get_context_data(**kwargs)
        return context


class CollectionView(DetailView):
    model = Collection
    template_name = 'collection_view.html'
    queryset = None

    def get_context_data(self, **kwargs):
        context = super(CollectionView, self).get_context_data(**kwargs)
        context['toc'] = self.get_object().list_toc_by_page()
        context['size'] = len(context['toc'])
        context['title'] = self.get_object().title_tuple()
        context['current_year'] = self.get_object().get_collection_date()
        context['special_issue'] = self.get_object().special_issue
        context['issue'] = self.get_object()
        return context


class ItemView(DetailView):
    model = Record
    template_name = 'item_view.html'

    def get_context_data(self, **kwargs):
        context = super(ItemView, self).get_context_data(**kwargs)
        context['item_data'] = self.get_object().as_display_dict()
        bitstream = context['item_data']['bitstream'][0]
        # PATCH to handle two different data structures in db (list or string)
        #   related to introduced modification to collect bitstreams as la ist 
        #   in utils/get_bitstream_url()


        context['bitstreams'] = []
        try:
            if not isinstance(bitstream, list):
                bitstream = [bitstream]    
            
            if bitstream:
                for bit_url in bitstream:
                    if not bit_url.startswith('https:'): 
                        bit_url = bit_url.replace('http://', 'https://', 1)
                    bit_url_name = bit_url[bit_url.rfind('/')+1:]
                    context['bitstreams'].append((bit_url, bit_url_name))
        except:
            pass

        # if bitstream:
        #     if not bitstream.startswith('https:'): 
        #         bitstream = bitstream.replace('http://', 'https://', 1)
        #     context['https_bitstream'] = bitstream
        #     context['pdf_filename'] = bitstream[bitstream.rfind('/')+1:]

        context['bitstream_extras'] = []
        try:
            bitstream_extras = context['item_data']['bitstream_extra'][0]
            for bit_url in bitstream_extras:
                if not bit_url.startswith('https:'): 
                    bit_url = bit_url.replace('http://', 'https://', 1)
                bit_url_name = bit_url[bit_url.rfind('/')+1:]
                context['bitstream_extras'].append((bit_url, bit_url_name))
        except Exception as e:
            pass
        
        # END PATCH




         
        # context['current_year'] = self.get_object().hdr_setSpec.get_collection_date()
        return context


class ItemViewFull(DetailView):
    model = Record
    template_name = 'item_view_full.html'

    def get_context_data(self, **kwargs):
        context = super(ItemViewFull, self).get_context_data(**kwargs)
        context['item_data'] = self.get_object().as_dict()
        return context


class PageView(BaseSideMenuMixin, DetailView):
    model = StoryPage
    template_name = 'page_view.html'
    context_object_name = 'page'

    def get(self, request, *args, **kwargs):
        if self.get_object().private:
            # will redirect to login required view
            return redirect('staff_page_view', item=self.get_object().id)
        return super(PageView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(PageView, self).get_context_data(*args, **kwargs)
        context['admin_edit'] = reverse('admin:lltsite_storypage_change', args=(self.get_object().id,))
        context['curr_page'] = self.get_object().id
        return context


class PageUpdateView(LoginRequiredMixin, UpdateView):
    model = StoryPage
    template_name = 'page_view_update.html'
    form_class = PageUpdateForm
    

class PageViewPrivate(LoginRequiredMixin, DetailView):
    model = StoryPage
    template_name = 'page_view.html'
    context_object_name = 'page'

    def get_context_data(self, *args, **kwargs):
        context = super(PageViewPrivate, self).get_context_data(*args, **kwargs)
        context['admin_edit'] = reverse('admin:lltsite_storypage_change', args=(self.get_object().id,))
        context['curr_page'] = self.get_object().id
        return context


class SearchHaystackView(SearchView):
    def get_context_data(self, *args, **kwargs):
        context = super(SearchHaystackView, self).get_context_data(*args, **kwargs)

        keylist = ['Assessment/Testing','Behavior-tracking Technology','Blended/Hybrid Learning and Teaching','Code Switching','Collaborative Learning','Computer-Mediated Communication','Concordancing','Corpus','Culture','Data-driven Learning','Digital Literacies','Discourse Analysis','Distance/Open Learning and Teaching','Eye Tracking','Feedback','Game-based Learning and Teaching','Grammar','Human-Computer Interaction','Indigenous Languages','Instructional Context','Instructional Design','Language for Special Purposes','Language Learning Strategies','Language Maintenance','Language Teaching Methodology','Learner Attitudes','Learner Autonomy','Learner Identity','Less Commonly Taught Languages','Listening','Meta Analysis','Mobile Learning','MOOCs','Multiliteracies','Natural Language Processing','Open Educational Resources','Pragmatics','Pronunciation','Reading','Research Methods','Social Context','Sociocultural Theory','Social Networking','Speaking','Speech Recognition','Speech Synthesis','Task-based Learning and Teaching','Teacher Education','Telecollaboration','Ubiquitous Learning and Teaching','Virtual Environments','Vocabulary','Writing']

        cols_length = len(keylist) // 3
        keytable = []
        for i in range(0, len(keylist), cols_length):
            keytable.append(keylist[i:i+cols_length])

        authorlist = []
        for i in MetadataElement.objects.filter(element_type='contributor.author'):
            for j in json.loads(i.element_data):                
                # swap the first and last so last appears after first.
                n = j.split(',')
                try:
                    authorlist.append((n[1].strip(), n[0].strip()))
                except:
                    pass
        
        authorlist = set(authorlist)
        authorlist = sorted(authorlist, key=lambda author: author[1].lower())

        # will create n sets of authors to be rendered in columns
        # cols_length = len(authorlist) / 6
        # authortable = []
        # for i in range(0, len(authorlist), cols_length):
        #     authortable.append(authorlist[i:i+cols_length])

        context['authortable'] = authorlist # using flat list for now. authortable an option if needed.
        context['keytable'] = keytable
        return context


class KeywordBrowseView(TemplateView):
    template_name = 'page_keyword_browse.html'

    def get_context_data(self, **kwargs):
        context = super(KeywordBrowseView, self).get_context_data(**kwargs)
        
        keylist = ['Assessment/Testing','Behavior-tracking Technology','Blended/Hybrid Learning and Teaching','Code Switching','Collaborative Learning','Computer-Mediated Communication','Concordancing','Corpus','Culture','Data-driven Learning','Digital Literacies','Discourse Analysis','Distance/Open Learning and Teaching','Eye Tracking','Feedback','Game-based Learning and Teaching','Grammar','Human-Computer Interaction','Indigenous Languages','Instructional Context','Instructional Design','Language for Special Purposes','Language Learning Strategies','Language Maintenance','Language Teaching Methodology','Learner Attitudes','Learner Autonomy','Learner Identity','Less Commonly Taught Languages','Listening','Meta Analysis','Mobile Learning','MOOCs','Multiliteracies','Natural Language Processing','Open Educational Resources','Pragmatics','Pronunciation','Reading','Research Methods','Social Context','Sociocultural Theory','Social Networking','Speaking','Speech Recognition','Speech Synthesis','Task-based Learning and Teaching','Teacher Education','Telecollaboration','Ubiquitous Learning and Teaching','Virtual Environments','Vocabulary','Writing']

        cols_length = len(keylist) / 3
        keytable = []
        for i in range(0, len(keylist), cols_length):
            keytable.append(keylist[i:i+cols_length])

        context['keytable'] = keytable
        return context


class SubscriberCreateView(CreateView):
    model = Subscriber
    template_name = 'subscriber_create.html'
    form_class= CreateSubscriberForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Begin reCAPTCHA validation with google.
        recaptcha_response = self.request.POST.get('g-recaptcha-response')
            
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret':  settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.urlencode(values)
        req = urllib.request(url, data)
        response = urlopen(req)
        result = json.load(response)
        # End reCAPTCHA validation 

        if result['success']:
            messages.success(self.request, 'Your email has been registered.', extra_tags='success')
            return super(SubscriberCreateView, self).form_valid(form)
        else:
            messages.error(self.request, 'Invalid reCAPTCHA. Please try again.', extra_tags='danger')
            return super(SubscriberCreateView, self).form_invalid(form)


class SubscriberListView(LoginRequiredMixin, ListView):
    model = Subscriber
    template_name = 'subscriber_list.html'

    def get_queryset(self):
        index = self.kwargs['alpha_index']
        return Subscriber.objects.filter(email__istartswith=index)

    def get_context_data(self, **kwargs):
        context = super(SubscriberListView, self).get_context_data(**kwargs)
        context['index'] = 'abcdefghijklmnopqrstuvwxyz'
        return context


class SubscriberListCsvView(LoginRequiredMixin, ListView):
    model = Subscriber

    def render_to_response(self, context, **response_kwargs):
        daystr = datetime.now().strftime('%Y-%m-%d-%I_%M_%p ')
        filename = 'llt-subscriber-list-' + daystr + '.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + filename
        writer = csv.writer(response)
        # alternate format: writer = csv.writer(response, delimiter=' ')
        for sub in context['object_list']:
            writer.writerow([sub.email.encode('utf8'), sub.first_name.encode('utf8'), sub.last_name.encode('utf8')])


        return response


class UpdateImpactFactorView(LoginRequiredMixin, UpdateView):
    model = ImpactFactor
    template_name = 'impact_factor_update.html'
    form_class = UpdateImpactFactorForm
    success_url = reverse_lazy('home')   


