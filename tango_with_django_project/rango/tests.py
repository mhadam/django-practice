from django.test import TestCase
from rango.models import Category, Page
from django.core.urlresolvers import reverse
from django.utils import timezone

def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c

def add_page(category, title, url):
    p = Page.objects.get_or_create(category=category, title=title, url=url)[0]
    p.save()
    return p

class CategoryMethodTests(TestCase):

    def test_ensure_views_are_positive(self):
        """
        ensure_views_are_positive should results True for categories where views are zero or positive
        """
        cat = Category(name='test', views=-1, likes=0)
        cat.save()
        self.assertEqual((cat.views >= 0), True)

    def test_slug_line_creation(self):
        """
        slug_line_creation checks to make sure that when we add a category an appropriate slug line is created
        i.e. "Random Category String" -> "random-category-string"
        """
        cat = Category(name='Random Category String')
        cat.save()
        self.assertEqual(cat.slug, 'random-category-string')

class IndexViewTests(TestCase):

    def test_index_view_with_no_categories(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no categories present.")
        self.assertQuerysetEqual(response.context['categories'], [])



    def test_index_view_with_categories(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """

        add_cat('test', 1, 1)
        add_cat('temp', 1, 1)
        add_cat('tmp', 1, 1)
        add_cat('tmp test temp', 1, 1)

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tmp test temp")
        
        num_cats = len(response.context['categories'])
        self.assertEqual(num_cats, 4)

    def test_visits_not_in_future(self):
        """
        test_visits_not_in_future checks that none of the page visit time/dates are in the future.
        """
        cat = add_cat('test', 1, 1)
        page_one = add_page(cat, 'test', 'http://www.test.com')
        page_two = add_page(cat, 'test2', 'http://www.test2.com')

        response_one = self.client.get(reverse('goto') + '?page_id=' + str(page_one.id))
        response_two = self.client.get(reverse('goto') + '?page_id=' + str(page_two.id))

        page_one = add_page(cat, 'test', 'http://www.test.com')
        page_two = add_page(cat, 'test2', 'http://www.test2.com')

        self.assertEqual(page_one.last_visit <= timezone.now(), True)
        self.assertEqual(page_two.last_visit <= timezone.now(), True)

    def test_visits_are_ordered(self):
        """
        test_visits_are_ordered checks that the first visit is before the last visit
        """
        cat = add_cat('test', 1, 1)
        page = add_page(cat, 'test', 'http://www.test.com')

        response = self.client.get(reverse('goto') + '?page_id=' + str(page.id))
        self.assertEqual(page.last_visit >= page.first_visit, True)
