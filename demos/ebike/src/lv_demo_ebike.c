/**
 * @file lv_demo_ebike.c
 *
 */

/*********************
 *      INCLUDES
 *********************/
#include "lv_demo_ebike.h"
#include "lv_demo_ebike_home.h"
#include "lv_demo_ebike_settings.h"
#include "lv_demo_ebike_stat.h"

/*********************
 *      DEFINES
 *********************/

/**********************
 *      TYPEDEFS
 **********************/

/**********************
 *  STATIC PROTOTYPES
 **********************/

/**********************
 *  STATIC VARIABLES
 **********************/
static void menu_item_click_event_cb(lv_event_t * e);
static lv_obj_t * main_cont;

/**********************
 *  GLOBAL VARIABLES
 **********************/
lv_subject_t ebike_subject_speed;

/**********************
 *      MACROS
 **********************/

/**********************
 *   GLOBAL FUNCTIONS
 **********************/

void lv_demo_ebike_create(void)
{
    lv_subject_init_int(&ebike_subject_speed, 0);
    lv_demo_ebike_stat_init();


    lv_display_t * display = lv_display_get_default();
    lv_theme_t * theme = lv_theme_simple_init(display);
    lv_display_set_theme(display, theme);

    lv_obj_set_flex_flow(lv_screen_active(), LV_FLEX_FLOW_ROW);
    lv_obj_remove_flag(lv_screen_active(), LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_set_style_text_color(lv_screen_active(), lv_color_white(), 0);

    LV_IMAGE_DECLARE(img_ebike_bg);
    lv_obj_t * bg = lv_image_create(lv_screen_active());
    lv_image_set_src(bg, &img_ebike_bg);
    lv_obj_align(bg, LV_ALIGN_CENTER, 0, 0);
    lv_obj_add_flag(bg, LV_OBJ_FLAG_IGNORE_LAYOUT);

    main_cont = lv_obj_create(lv_screen_active());
    lv_obj_set_height(main_cont, lv_pct(100));
    lv_obj_set_flex_grow(main_cont, 1);
    lv_obj_set_style_bg_opa(main_cont, 0, 0);

    lv_obj_t * menu_cont = lv_obj_create(lv_screen_active());
    lv_obj_set_style_bg_color(menu_cont, lv_color_black(), 0);
    lv_obj_set_size(menu_cont, 44, lv_pct(100));
    lv_obj_align(menu_cont, LV_ALIGN_RIGHT_MID, 44, 0);
    lv_obj_set_flex_flow(menu_cont, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(menu_cont, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_set_style_pad_gap(menu_cont, 32, 0);

    //    lv_demo_ebike_home_create(main_cont);
    lv_demo_ebike_stat_create(main_cont);

    LV_IMAGE_DECLARE(img_ebike_settings);
    lv_obj_t * icon1 = lv_image_create(menu_cont);
    lv_image_set_src(icon1, &img_ebike_settings);
    lv_obj_add_event_cb(icon1, menu_item_click_event_cb, LV_EVENT_CLICKED, NULL);
    lv_obj_set_ext_click_area(icon1, 32);
    lv_obj_add_flag(icon1, LV_OBJ_FLAG_CLICKABLE);

    LV_IMAGE_DECLARE(img_ebike_stat);
    lv_obj_t * icon2 = lv_image_create(menu_cont);
    lv_image_set_src(icon2, &img_ebike_stat);
    lv_obj_add_event_cb(icon2, menu_item_click_event_cb, LV_EVENT_CLICKED, NULL);
    lv_obj_set_ext_click_area(icon2, 32);
    lv_obj_add_flag(icon2, LV_OBJ_FLAG_CLICKABLE);

    LV_IMAGE_DECLARE(img_ebike_home);
    lv_obj_t * icon3 = lv_image_create(menu_cont);
    lv_image_set_src(icon3, &img_ebike_home);
    lv_obj_add_event_cb(icon3, menu_item_click_event_cb, LV_EVENT_CLICKED, NULL);
    lv_obj_set_ext_click_area(icon3, 32);
    lv_obj_add_flag(icon3, LV_OBJ_FLAG_CLICKABLE);
}

/**********************
 *   STATIC FUNCTIONS
 **********************/


static void menu_item_click_event_cb(lv_event_t * e)
{

    lv_obj_clean(main_cont);

    lv_obj_t  * icon = lv_event_get_target(e);
    uint32_t idx = lv_obj_get_index(icon);
    switch(idx) {
        case 0:
            lv_demo_ebike_settings_create(main_cont);
            break;
        case 1:
            lv_demo_ebike_stat_create(main_cont);
            break;
        case 2:
            lv_demo_ebike_home_create(main_cont);
            break;
        default:
            break;
    }
}
