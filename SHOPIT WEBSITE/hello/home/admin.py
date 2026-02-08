from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Contact, ProductCategory, Product, ProductImage, ProductVariant,
    ProductReview, Order, OrderItem, Coupon, UserProfile, Address,
    Wishlist, SupportTicket, SupportMessage, Return
)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('created_at',)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'created_at', 'product_image')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline, ProductVariantInline]
    
    def product_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    product_image.short_description = 'Preview'


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username')
    readonly_fields = ('created_at',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'name', 'email', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'payment_method')
    search_fields = ('order_id', 'name', 'email', 'phone')
    readonly_fields = ('order_id', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {'fields': ('order_id', 'user', 'created_at', 'updated_at')}),
        ('Customer Info', {'fields': ('name', 'email', 'phone')}),
        ('Shipping', {'fields': ('address', 'tracking_number')}),
        ('Payment', {'fields': ('total_amount', 'delivery_fee', 'discount_amount', 'payment_method')}),
        ('Status', {'fields': ('status',)}),
    )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'discount_amount', 'is_active', 'valid_till', 'current_uses', 'max_uses')
    list_filter = ('is_active', 'valid_till')
    search_fields = ('code',)
    readonly_fields = ('current_uses',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_of_birth')
    search_fields = ('user__username', 'phone')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_type', 'city', 'state', 'is_default')
    list_filter = ('address_type', 'city', 'state')
    search_fields = ('user__username', 'city', 'state')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'product_count')
    search_fields = ('user__username',)
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0
    readonly_fields = ('user', 'message', 'created_at')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'user__username')
    inlines = [SupportMessageInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'status', 'refund_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_id',)
    readonly_fields = ('created_at',)
