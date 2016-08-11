from django.test import TestCase
from django.core.urlresolvers import reverse
from .models import Category, Page
from datetime import datetime


def add_category(name, views, likes):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c


class CategoryMethodTests(TestCase):

    def test_ensure_views_are_positive(self):
        """True for nonnegative views value"""
        cat = Category(name='test1', views=-1, likes=0)
        cat.save()
        self.assertEqual((cat.views >= 0), True)

    def test_slug_line_creation(self):
        cat = Category(name='Random Category STRING')
        cat.save()
        self.assertEqual(cat.slug, 'random-category-string')

    def test_ensure_positive_views_are_saved(self):
        """True if value is the same"""
        cat = Category(name='test2', views=10, likes=0)
        cat.save()
        new_cat = Category.objects.get(name='test2')
        self.assertEqual(new_cat.views, 10)


class PageMethodsTest(TestCase):
    def test_visit_time_in_the_past(self):
        c = add_category('test1', 0, 0)
        page = Page(title='test', url='http://example.com', category=c)
        page.save()
        # time_after = datetime.now()
        # self.assertGreater(time_after, page.first_visit)
        # self.assertGreater(time_after, page.last_visit)

    def test_last_visit_time_gte_first_visit_time(self):
        c = add_category('test1', 0, 0)
        page = Page(title='test1', url='http://example.com', category=c)
        page.save()
        self.client.get('/rango/goto?page_id={}'.format(page.id))
        self.assertGreater(page.last_visit, page.first_visit)


class IndexViewTests(TestCase):
    def test_index_with_no_categories(self):
        response = self.client.get(reverse('rango:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No categories present.')
        self.assertQuerysetEqual(response.context['categories'], [])

    def test_index_view_with_categories(self):
        add_category('test', 1, 1)
        add_category('temp', 1, 1)
        add_category('test2', 1, 1)
        add_category('temp test', 1, 1)

        response = self.client.get(reverse('rango:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'temp test')

        num_cats = len(response.context['categories'])
        self.assertEqual(num_cats, 4)

