/*
 * Watchdog driver for the Haliburton
 *
 * Copyright (C) 2017 Celestica Corp.
 *
 *  This program is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU General Public License
 *  as published by the Free Software Foundation; either version
 *  2 of the License, or (at your option) any later version.
 */

#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/types.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/platform_device.h>
#include <linux/watchdog.h>
#include <linux/uaccess.h>
#include <linux/gpio.h>
#include <linux/io.h>
#include <linux/delay.h>

#define DRIVER_NAME "e1030.wdt"

#define WDI_TIME_SET	0x0110
#define WDI_RST_CON		0x0111
#define WDI_MASK_BIT	0x01
#define WDI_RST_SOURCE	0x0112
#define WDI_GPIO_DIR	0x504
#define WDI_GPIO		0x508

#define GPIO_PIN_TICK	15

static bool nowayout = WATCHDOG_NOWAYOUT;

struct e1030_wdt_drvdata {
	struct watchdog_device wdt;
	struct mutex lock;
};

static struct resource e1030_wdt_resources[] = {
        {
                .flags  = IORESOURCE_IO,
        },
};

static void e1030_wdt_dev_release( struct device * dev)
{
        return;
}

static struct platform_device e1030_wdt_dev = {
        .name           = DRIVER_NAME,
        .id             = -1,
        .num_resources  = ARRAY_SIZE(e1030_wdt_resources),
        .resource       = e1030_wdt_resources,
        .dev = {
                        .release = e1030_wdt_dev_release,
        }
};

static int e1030_wdt_set_timeout(struct watchdog_device *wdt_dev, unsigned int timeout)
{
		struct e1030_wdt_drvdata *drvdata = watchdog_get_drvdata(wdt_dev);
		mutex_lock(&drvdata->lock);

		// timout 0x0:200ms  0x1:30s  0x2:60s  0x3:180s
		if(timeout < 4){
			outb(timeout, WDI_TIME_SET);
			drvdata->wdt.timeout = timeout;
		}

		mutex_unlock(&drvdata->lock);

		return 0;
}

static int e1030_wdt_start(struct watchdog_device *wdt_dev)
{
        struct e1030_wdt_drvdata *drvdata = watchdog_get_drvdata(wdt_dev);
        unsigned char reset_ctrl = 0x00;
        unsigned long gpio ,dir;

        mutex_lock(&drvdata->lock);

        gpio = inl(WDI_GPIO);
        gpio |= 1 << GPIO_PIN_TICK;
        outl(gpio, WDI_GPIO);

        outl((inl(WDI_GPIO_DIR) & (~(1 << GPIO_PIN_TICK))), WDI_GPIO_DIR);

        reset_ctrl = inb(WDI_RST_CON);

        gpio = inl(WDI_GPIO);
        gpio &= ~(1 << GPIO_PIN_TICK);
        outl_p( gpio, WDI_GPIO );

        mdelay(10);

        gpio = inl(WDI_GPIO);
        gpio |= (1 << GPIO_PIN_TICK);
        outl_p( gpio, WDI_GPIO );

        reset_ctrl |= WDI_MASK_BIT;
        outb(reset_ctrl, WDI_RST_CON);

        mutex_unlock(&drvdata->lock);

        return 0;
}

static int e1030_wdt_stop(struct watchdog_device *wdt_dev)
{
        struct e1030_wdt_drvdata *drvdata = watchdog_get_drvdata(wdt_dev);
        unsigned long reset_ctrl;

        mutex_lock(&drvdata->lock);

        reset_ctrl = inb(WDI_RST_CON);
        reset_ctrl &= WDI_MASK_BIT;
        outb(reset_ctrl, WDI_RST_CON);

        mutex_unlock(&drvdata->lock);

        return 0;
}

static int e1030_wdt_ping(struct watchdog_device *wdt_dev)
{
        struct e1030_wdt_drvdata *drvdata = watchdog_get_drvdata(wdt_dev);
        unsigned long gpio;

        mutex_lock(&drvdata->lock);

        gpio = inl(WDI_GPIO);
        gpio &= ~(1 << 15);
        outl_p( gpio, WDI_GPIO );

        mdelay(10);

        gpio = inl(WDI_GPIO);
        gpio |= (1 << 15);
        outl_p( gpio, WDI_GPIO );

        mutex_unlock(&drvdata->lock);

        return 0;
}


static const struct watchdog_info e1030_wdt_info = {
        .options = WDIOF_KEEPALIVEPING | WDIOF_MAGICCLOSE | WDIOF_SETTIMEOUT,
        .identity = "e1030 Watchdog",
};

static const struct watchdog_ops e1030_wdt_ops = {
        .owner = THIS_MODULE,
        .start = e1030_wdt_start,
        .stop = e1030_wdt_stop,
        .ping = e1030_wdt_ping,
        .set_timeout = e1030_wdt_set_timeout
};

static int e1030_wdt_probe(struct platform_device *pdev)
{
        struct e1030_wdt_drvdata *drvdata;
        int ret;

        drvdata = devm_kzalloc(&pdev->dev, sizeof(*drvdata),
                                   GFP_KERNEL);
        if (!drvdata) {
                ret = -ENOMEM;
                goto err;
        }

        mutex_init(&drvdata->lock);

        drvdata->wdt.info = &e1030_wdt_info;
        drvdata->wdt.ops = &e1030_wdt_ops;

        watchdog_set_nowayout(&drvdata->wdt, nowayout);
        watchdog_set_drvdata(&drvdata->wdt, drvdata);

        ret = watchdog_register_device(&drvdata->wdt);
        if (ret != 0) {
                dev_err(&pdev->dev, "watchdog_register_device() failed: %d\n",
                        ret);
                goto err;
        }

        platform_set_drvdata(pdev, drvdata);

err:
        return ret;
}

static int e1030_wdt_remove(struct platform_device *pdev)
{
        struct e1030_wdt_drvdata *drvdata = platform_get_drvdata(pdev);

        watchdog_unregister_device(&drvdata->wdt);

        return 0;
}

static struct platform_driver e1030_wdt_drv = {
        .probe = e1030_wdt_probe,
        .remove = e1030_wdt_remove,
        .driver = {
                .name = DRIVER_NAME,
        },
};


int e1030_wdt_init(void)
{
	platform_device_register(&e1030_wdt_dev);
	platform_driver_register(&e1030_wdt_drv);

	return 0;
}

void e1030_wdt_exit(void)
{
	platform_driver_unregister(&e1030_wdt_drv);
	platform_device_register(&e1030_wdt_dev);
}

module_init(e1030_wdt_init);
module_exit(e1030_wdt_exit);

MODULE_AUTHOR("Pariwat Leamsumran <pleamsum@celestica.com>");
MODULE_DESCRIPTION("Haliburton E1030 Watchdog");
MODULE_LICENSE("GPL");
MODULE_ALIAS("platform:haliburton-watchdog");
